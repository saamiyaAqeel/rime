// This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
// See LICENSE.txt for full details.
// Copyright 2023 Telemarq Ltd

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    server : {
        port: 3000,
        strictPort: true,
    },
    envDir: './',
    envPrefix: 'RIME',
    clearScreen: false,
})
