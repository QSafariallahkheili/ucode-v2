import { fileURLToPath, URL } from 'url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vuetify from 'vite-plugin-vuetify';


export default defineConfig({
  server: {
    host: true,
    port: 8080
  },
  plugins: [
		vue(),
		vuetify({ autoImport: true }),
],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
     
    },
    
  }
})
