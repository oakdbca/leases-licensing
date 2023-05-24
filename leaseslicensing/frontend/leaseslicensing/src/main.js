// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
//import Vue from 'vue'

import { createApp } from 'vue';
import router from './router';
import App from './App';
import helpers from '@/utils/helpers';
import CKEditor from '@ckeditor/ckeditor5-vue';
import { extendMoment } from 'moment-range';

import govVue3Components from '@dbca/gov-vue3-components';
import '@dbca/gov-vue3-components/dist/library.css';

import 'datatables.net-bs5';
import 'datatables.net-buttons-bs5';
import 'datatables.net-responsive-bs5';
import 'datatables.net-buttons/js/dataTables.buttons.js';
import 'datatables.net-buttons/js/buttons.html5.js';
import 'select2';

import 'sweetalert2/dist/sweetalert2.css';

import 'jquery-validation';

// eslint-disable-next-line no-undef
extendMoment(moment);

import '@/../node_modules/@fortawesome/fontawesome-free/css/all.min.css';
import 'select2/dist/css/select2.min.css';
import 'select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.min.css';
import '@/../node_modules/datatables.net-bs5/css/dataTables.bootstrap5.min.css';
import '@/../node_modules/datatables.net-responsive-bs5/css/responsive.bootstrap5.min.css';
import '@/../node_modules/vue-multiselect/dist/vue-multiselect.css';

// Add CSRF Token to every request
const customHeaders = new Headers({
    'X-CSRFToken': helpers.getCookie('csrftoken'),
});
const customHeadersJSON = new Headers({
    'X-CSRFToken': helpers.getCookie('csrftoken'),
    'Content-Type': 'application/json',
});
// eslint-disable-next-line no-global-assign
fetch = (originalFetch => {
    return (...args) => {
        if (args.length > 1) {
            if (typeof (args[1].body) === 'string') {
                args[1].headers = customHeadersJSON;
            } else {
                args[1].headers = customHeaders;
            }
        }
        const result = originalFetch.apply(this, args);
        return result;
    };
})(fetch);

const app = createApp(App);

app.use(CKEditor);
app.use(router);
app.use(govVue3Components);
router.isReady().then(() => app.mount('#app'));
