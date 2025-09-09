import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.message));
  page.on('response', response => {
    if (response.url().includes('/login') || response.url().includes('/auth') || response.url().includes('/users/')) {
      console.log(`API response: ${response.status()} from ${response.url()}`);
      response.text().then(body => console.log(`API response body: ${body}`));
    }
  });
  await page.goto('http://localhost:3000/login');
  await page.waitForSelector('input[placeholder="사용자명을 입력하세요"]', { timeout: 30000 });
  // 로그인 입력
  await page.getByPlaceholder('사용자명을 입력하세요').fill('admin'); // 테스트 계정
  await page.getByPlaceholder('비밀번호를 입력하세요').fill('admin123'); // 실제 비밀번호로 변경 필요
  await page.getByRole('button', { name: '로그인' }).click(); // 로그인 버튼 클릭
  // 리다이렉트 확인
  try {
    await page.waitForURL('**/dashboard', { timeout: 30000 });
    console.log('Redirected to:', page.url());
  } catch (error) {
    console.log('Redirect timeout. Current URL:', page.url());
  }
  await page.waitForTimeout(5000);
  await browser.close();
})();