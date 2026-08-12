import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// Dentro de docker-compose, el backend vive en otro contenedor y no es
// accesible como "localhost" — se resuelve por el nombre del servicio.
// BACKEND_INTERNAL_URL se define en docker-compose.yml; en local (npm run dev
// sin Docker) simplemente no existe y se usa localhost.
const backendTarget = process.env.BACKEND_INTERNAL_URL || 'http://localhost:8000'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'favicon-32.png', 'apple-touch-icon.png'],
      manifest: {
        name: 'FincasPro — Gestión de Fincas',
        short_name: 'FincasPro',
        description: 'Gestión de incidencias, paquetería, llaves y avisos de la comunidad.',
        theme_color: '#131217',
        background_color: '#131217',
        display: 'standalone',
        start_url: '/',
        scope: '/',
        lang: 'es',
        icons: [
          { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: '/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
        ]
      },
      workbox: {
        // El shell de la app (JS/CSS/HTML) se cachea para carga instantánea offline.
        // Las llamadas a /api y /uploads NUNCA se cachean: los datos de tickets,
        // paquetes y avisos siempre deben venir frescos del servidor.
        navigateFallbackDenylist: [/^\/api/, /^\/uploads/],
        runtimeCaching: [
          {
            urlPattern: /^\/api\//,
            handler: 'NetworkOnly'
          }
        ]
      },
      devOptions: {
        enabled: false
      }
    })
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': backendTarget,
      '/uploads': backendTarget
    }
  }
})
