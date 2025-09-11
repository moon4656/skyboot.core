import { createApp } from 'vue'
import { createVuesticEssential } from 'vuestic-ui'
import 'vuestic-ui/css'
import 'material-icons/iconfont/material-icons.css'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { skybootTheme } from './styles/theme'

const app = createApp(App)

// Pinia 스토어
app.use(createPinia())

// Vue Router
app.use(router)

// Vuestic UI with Custom Theme
app.use(createVuesticEssential({
  config: {
    colors: skybootTheme.colors,
    components: skybootTheme.components,
    icons: [
      {
        name: 'material-icons',
        resolve: ({ icon }) => ({ class: 'material-icons', content: icon })
      }
    ]
  }
}))

app.mount('#app')
