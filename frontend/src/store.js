// This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
// See LICENSE.txt for full details.
// Copyright 2023 Telemarq Ltd

import { ref, computed } from 'vue';
import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client/core'
import { useQuery, useMutation, provideApolloClient } from '@vue/apollo-composable'
import { useLocalStorage } from '@vueuse/core'
import gql from 'graphql-tag'

/* GraphQL integration */
const backendUrl = import.meta.env.RIME_BACKEND || '';
export const apolloClient = new ApolloClient({
    link: createHttpLink({
        uri: backendUrl + '/graphql',
    }),
    cache: new InMemoryCache(),
});

provideApolloClient(apolloClient);

export const { result: devicesGqlResult, refetch: devicesGqlRefetch } = useQuery( gql`
  query getDevices {
	  devices {
		  id
		  is_subset
          is_locked
		  country_code
	  }
  }
`);

const { mutate: setDevicePropertiesMutation } = useMutation( gql`
	mutation setDeviceProperties($id: String!, $properties: SetDeviceProperties!) {
		setDeviceProperties(deviceId: $id, deviceProperties: $properties)
	}
`);

const { mutate: deleteDeviceMutation } = useMutation( gql`
	mutation deleteDevice($id: String!) {
		deleteDevice(deviceId: $id)
	}
`);


export const devices = computed(() => {
    if(!devicesGqlResult.value || !devicesGqlResult.value.devices) {
        return [];
    }
    return devicesGqlResult.value.devices;
});

const selectedDevices = useLocalStorage('selectedDevices', []);

export const activeDevices = computed(() => {
    if(!devicesGqlResult.value || !devicesGqlResult.value.devices) {
        return [];
    }

    return devicesGqlResult.value.devices.filter(d => selectedDevices.value.includes(d.id)).map(d => d.id);
});

export async function setDeviceSelected(id, isSelected) {
    if(isSelected) {
        selectedDevices.value.push(id);
    } else {
        selectedDevices.value = selectedDevices.value.filter(d => d !== id);
    }
}

export async function deleteDevice(id) {
    await deleteDeviceMutation({ "id": id });
    await devicesGqlRefetch();
}

export const contactsFilter = ref({ });
export const eventsFilter = ref({ });

export function hasEventsFilter() {
    return Object.keys(eventsFilter.value).length > 0;
}

export function setFilter(filter) {
    eventsFilter.value = filter;
}

/* Watch the devices list by refreshing. TODO: Use subscriptions */
export function enableWatchers() {
    setInterval(() => {
        devicesGqlRefetch();
    }, 2000);
}
