// This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
// See LICENSE.txt for full details.
// Copyright 2023 Telemarq Ltd

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from "node:url";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    server : {
        host: 'localhost',
        port: 3000,
        strictPort: true,
    },
    envDir: './',
    envPrefix: 'RIME',
    clearScreen: false,
    // resolve: {
    //     alias: {
    //      "@": fileURLToPath(new URL("./src", import.meta.url)),
    //     },
    //    },
    // optimizeDeps: {
    //     include: ["vue2-google-maps", "fast-deep-equal"],
    //    },
})

