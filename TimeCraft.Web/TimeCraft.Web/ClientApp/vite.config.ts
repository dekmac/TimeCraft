import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import mkcert from 'vite-plugin-mkcert'

// https://vite.dev/config/
export default defineConfig({
    plugins: [react(), mkcert()],
    server: {
        port: 44445,
        strictPort: true,
        proxy: {
            "/api": {
                target: "https://localhost:5001",
                changeOrigin: true,
                secure: false,
            },
        },
    },
    build: {
        outDir: 'dist',
        sourcemap: true
    }
})
