// This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
// See LICENSE.txt for full details.
// Copyright 2023 Telemarq Ltd

import { createApp, provide } from 'vue'
import './style.css'
import { createPinia } from 'pinia'
import { DefaultApolloClient } from '@vue/apollo-composable'
import App from './App.vue'
import { apolloClient } from './store'

const app = createApp(App);

/* Store */
const pinia = createPinia();
app.use(pinia);

app.provide(DefaultApolloClient, apolloClient);

app.mount('#app');
