import { createApp, readonly } from 'vue'
import { createVuestic } from 'vuestic-ui'
import 'vuestic-ui/css'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// readonly를 전역으로 설정
if (typeof window !== 'undefined') {
  window.readonly = readonly
}

const app = createApp(App)

// Pinia 스토어 설정
app.use(createPinia())

// Vue Router 설정
app.use(router)

// Vuestic UI 설정
app.use(createVuestic())

app.mount('#app')
