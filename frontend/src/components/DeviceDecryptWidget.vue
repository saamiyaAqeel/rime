<!--
This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
See LICENSE.txt for full details.
Copyright 2023 Telemarq Ltd
-->

<!--
Component responsible for displaying an input field and making a mutation
request to the GraphQL API.
-->

<script setup>
import { ref } from 'vue';

import { useMutation } from '@vue/apollo-composable';
import gql from 'graphql-tag';

const { mutate: decryptDevice } = useMutation(gql`
  mutation decryptDevice($deviceId: String!, $passphrase: String!) {
    decryptDevice(deviceId: $deviceId, passphrase: $passphrase)
  }
`);

const props = defineProps({
  deviceId: String,
});

const showPassphraseInput = ref(false);
const passphrase = ref('');
</script>

<template>
  <div class="decrypt" @click="showPassphraseInput = !showPassphraseInput">&#128273;</div>
  <div class="container" v-if="showPassphraseInput">
    <input type="password" v-model="passphrase" placeholder="Type passphrase..." />
    <button
      @click="
        decryptDevice({
          deviceId: props.deviceId,
          passphrase: passphrase,
        })
      "
    >
      Decrypt
    </button>
  </div>
</template>

<style scoped>
.decrypt {
  display: inline-block;
  font-size: 14px;
  text-align: center;
  cursor: pointer;
}

.container {
  display: grid;
  grid-template-columns: 70% 30%;
}
</style>
