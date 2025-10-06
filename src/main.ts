import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// Import Quasar
import { Quasar } from 'quasar'
import '@quasar/extras/material-icons/material-icons.css'
import 'quasar/dist/quasar.css'

const app = createApp(App)

app.use(Quasar, {
  plugins: {} // import Quasar plugins and add here
})

app.mount('#app')
