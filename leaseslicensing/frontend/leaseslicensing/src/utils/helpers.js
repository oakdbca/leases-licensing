module.exports = {
    // Handle fetch get and post requests by stringifying JSON input and returning a JSON object
    fetchWrapper: async function (url, method, data) {
        let parsedMethod = null;
        if (method) {
            parsedMethod = method.trim().toUpperCase();
        }
        let response = null;
        if (!url) {
            throw 'You must specify a url';
        }
        if (arguments.length > 1) {
            if (!(['POST', 'GET'].includes(parsedMethod))) {
                throw 'HTTP method must be GET or POST';
            }
            if (parsedMethod === 'POST' && !data) {
                throw 'POST method requires data argument';
            }
        }
        if (!parsedMethod || parsedMethod === 'GET') {
            try {
                const getResponse = await fetch(url);
                response = await getResponse.json();
            } catch (error) {
                console.error(error);
            }
        } else if (parsedMethod === 'POST') {
            try {
                const postResponse = await fetch(url, {
                    method: parsedMethod,
                    body: JSON.stringify(data)
                });
                response = await postResponse.json();
            } catch (error) {
                console.error(error);
            }
        }
        return response;
    },

    formatError: function (err) {
        let returnStr = '';
        // object {}
        if (typeof (err.body) === 'object' && !Object.prototype.hasOwnProperty.call(err.body, 'length')) {
            for (const key of Object.keys(err.body)) {
                returnStr += `${key}: ${err.body[key]} <br/>`;
            }
            // array
        } else if (typeof (err.body) === 'object') {
            returnStr = err.body[0];
            // string
        } else {
            returnStr = err.body;
        }
        return returnStr;
    },
    apiError: function (resp) {
        var error_str = '';
        if (resp.status === 400) {
            try {
                let obj = JSON.parse(resp.responseText);
                error_str = obj.non_field_errors[0].replace(/[[\]"]/g, '');
            }
            catch (e) {
                error_str = resp.responseText.replace(/[[\]"]/g, '');
            }
        }
        else if (resp.status === 404) {
            error_str = 'The resource you are looking for does not exist.';
        }
        else {
            error_str = resp.responseText.replace(/[[\]"]/g, '');
        }
        return error_str;
    },
    apiVueResourceError: function (resp) {
        var error_str = '';
        var text = null;
        if (resp.status === 400) {
            if (Array.isArray(resp.body)) {
                text = resp.body[0];
            }
            else if (typeof resp.body == 'object') {
                text = resp.body;
            }
            else {
                text = resp.body;
            }

            if (typeof text == 'object') {
                if (Object.prototype.hasOwnProperty.call(text, 'non_field_errors')) {
                    error_str = text.non_field_errors[0].replace(/[[\]"]/g, '');
                } else {
                    console.log('text');
                    console.log(text);
                    for (let key in text) {
                        error_str += key + ': ' + text[key] + '<br/>';
                    }
                }
            }
            else {
                error_str = text.replace(/[[\]"]/g, '');
                error_str = text.replace(/^['"](.*)['"]$/, '$1');
            }
        }
        else if (resp.status === 404) {
            error_str = 'The resource you are looking for does not exist.';
        }
        console.log('apiVueResourceError: ', error_str);
        return error_str;
    },

    goBack: function (vm) {
        vm.$router.go(window.history.back());
    },
    copyObject: function (obj) {
        return JSON.parse(JSON.stringify(obj));
    },
    getCookie: function (name) {
        var value = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1)
                    .trim() === (name + '=')) {
                    value = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return value;
    },
    namePopover: function ($, vmDataTable) {
        vmDataTable.on('mouseover', '.name_popover', function () {
            $(this).popover('show');
            $(this).on('mouseout', function () {
                $(this).popover('hide');
            });
        });
    },
    add_endpoint_json: function (string, addition) {
        let res = string.split('.json');
        let endpoint = res[0] + '/' + addition + '.json';
        endpoint = endpoint.replace('//', '/');  // Remove duplicated '/' just in case
        return endpoint;
    },
    add_endpoint_join: function (api_string, addition) {
        // assumes api_string has trailing forward slash '/' character required for POST
        let endpoint = api_string + addition;
        endpoint = endpoint.replace('//', '/');  // Remove duplicated '/' just in case
        // if the last character is not a forward slash then add one
        if (endpoint.slice(-1) != '/') {
            endpoint += '/';
        }
        return endpoint;
    },
    dtPopover: function (value, truncate_length = 30, trigger = 'hover') {
        var ellipsis = '...',
            truncated = _.truncate(value, { // eslint-disable-line no-undef
                length: truncate_length,
                omission: ellipsis,
                separator: ' '
            }),
            result = '<span>' + truncated + '</span>',
            popTemplate = _.template('<a href="#" ' + // eslint-disable-line no-undef
                'role="button" ' +
                'data-toggle="popover" ' +
                'data-trigger="' + trigger + '" ' +
                'data-placement="top auto"' +
                'data-html="true" ' +
                'data-content="<%= text %>" ' +
                '>more</a>');
        if (_.endsWith(truncated, ellipsis)) { // eslint-disable-line no-undef
            result += popTemplate({
                text: value
            });
        }
        return result;
    },
    dtPopoverCellFn: function (cell) {
        $(cell).find('[data-toggle="popover"]')
            .popover()
            .on('click', function (e) {
                e.preventDefault();
                return true;
            });
    },
    processError: async function (err) {
        console.log(err);
        let errorText = '';
        if (err.body.non_field_errors) {
            console.log('non_field_errors');
            // When non field errors raised
            for (let i = 0; i < err.body.non_field_errors.length; i++) {
                errorText += err.body.non_field_errors[i] + '<br />';
            }
        } else if (Array.isArray(err.body)) {
            console.log('isArray');
            // When serializers.ValidationError raised
            for (let i = 0; i < err.body.length; i++) {
                errorText += err.body[i] + '<br />';
            }
        } else {
            console.log('else');
            // When field errors raised
            for (let field_name in err.body) {
                if (Object.prototype.hasOwnProperty.call(err.body, field_name)) {
                    errorText += field_name + ':<br />';
                    for (let j = 0; j < err.body[field_name].length; j++) {
                        errorText += err.body[field_name][j] + '<br />';
                    }
                }
            }
        }
        await swal('Error', errorText, 'error'); // eslint-disable-line no-undef
    },
    post_and_redirect: function (url, postData) {
        /* http.post and ajax do not allow redirect from Django View (post method),
           this function allows redirect by mimicking a form submit.

           usage:  vm.post_and_redirect(vm.application_fee_url, {'csrfmiddlewaretoken' : vm.csrf_token});
        */
        var postFormStr = '<form method="POST" action="' + url + '">';

        for (let key in postData) {
            if (Object.prototype.hasOwnProperty.call(postData, key)) {
                postFormStr += '<input type="hidden" name="' + key + '" value="' + postData[key] + '">';
            }
        }
        postFormStr += '</form>';
        let formElement = $(postFormStr);
        $('body').append(formElement);
        $(formElement).submit();
    },
    enablePopovers: function () {
        let popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            new bootstrap.Popover(popoverTriggerEl); // eslint-disable-line no-undef
        });
    },
    parseFetchError: async function (response) {
        let errorString = '';
        let resData = '';
        try {
            resData = await response.json();
        } catch (error) {
            console.error(error);
            resData = response;
        }
        console.log(resData);
        if (Array.isArray(resData)) {
            for (let i = 0; i < resData.length; i++) {
                errorString += (resData[i] + '<br>');
            }
        } else {
            // Stringify obj
            errorString = JSON.stringify(resData);
        }
        console.log(errorString);
        return errorString;
    },
    getErrorStringFromResponseData(data) {
        let errorString = '';
        if (Array.isArray(data)) {
            for (let i = 0; i < data.length; i++) {
                errorString += (data[i] + '<br>');
            }
        } else {
            errorString = JSON.stringify(data);
        }
        return errorString;
    },
    getFileIconClass: function (filepath, additional_class_names = []) {
        let ext = filepath.split('.').pop().toLowerCase();
        let classname = additional_class_names;

        if (['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif',].includes(ext)) {
            classname.push('bi-file-image-fill');
        } else if (['pdf',].includes(ext)) {
            classname.push('bi-file-pdf-fill');
        } else if (['doc', 'docx',].includes(ext)) {
            classname.push('bi-file-word-fill');
        } else if (['xls', 'xlsx',].includes(ext)) {
            classname.push('bi-file-excel-fill');
        } else if (['txt', 'text',].includes(ext)) {
            classname.push('bi-file-text-fill');
        } else if (['rtf',].includes(ext)) {
            classname.push('bi-file-richtext-fill');
        } else if (['mp3', 'mp4'].includes(ext)) {
            classname.push('bi-file-play-fill');
        } else {
            classname.push('bi-file_fill');
        }

        return classname.join(' ');
    },
    formatABN: function (abn) {
        if (abn.length == 11) {
            return abn.slice(0, 2) + ' ' + abn.slice(2, 5) + ' ' + abn.slice(5, 8) + ' ' + abn.slice(8, 11);
        } else {
            return abn;
        }
    },
    formatACN: function (acn) {
        if (acn.length == 9) {
            return acn.slice(0, 3) + ' ' + acn.slice(3, 6) + ' ' + acn.slice(6, 9);
        } else {
            return acn;
        }
    },
    formatABNorACN: function (input) {
        if (input.length == 11) {
            return this.formatABN(input);
        } else if (input.length == 9) {
            return this.formatACN(input);
        } else {
            return input;
        }
    },
    validateABN: function (abn) {
        if (abn.length != 11) {
            return false;
        }
        let sum = 0;
        for (let i = 0; i < 11; i++) {
            let weight = 11 - i;
            sum += weight * abn[i];
        }
        return sum % 89 == 0;
    },
    validateACN: function (acn) {
        if (acn.length != 9) {
            return false;
        }
        let sum = 0;
        for (let i = 0; i < 8; i++) {
            let weight = 8 - i;
            sum += weight * acn[i];
        }
        return sum % 89 == 0;
    },
    isValidABNorACN: function (input) {
        if (input.length == 11) {
            return this.validateABN(input);
        } else if (input.length == 9) {
            return this.validateACN(input);
        } else {
            return false;
        }
    },
    formatDateForAPI: function (data, format = 'DD/MM/YYYY') {
        return data ? moment(data).format(format) : ''; // eslint-disable-line no-undef
    },
};
