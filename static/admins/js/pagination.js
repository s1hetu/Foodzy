function getParams(url = window.location) {
            let params = {};

            new URL(url).searchParams.forEach(function (val, key) {
                if (params[key] !== undefined) {
                    if (!Array.isArray(params[key])) {
                        params[key] = [params[key]];
                    }
                    params[key].push(val);
                } else {
                    params[key] = val;
                }
            });

            return params;

        }

        $(function () {
            let getParameter = getParams();
            let mainQueryParams = new URLSearchParams();

            let page = getParameter['page']
            if (page) {
                mainQueryParams.set("page", page);
            }

            let page_number_links = $('.page_number_link');
            if (page_number_links.length) {
                for (let i = 0; i < page_number_links.length; i++) {
                    let queryParams = mainQueryParams
                    queryParams.set("page", $(page_number_links[i]).attr('href'));
                    let next_url = location.protocol + '//' + location.host + location.pathname + "?" + queryParams.toString()
                    $(page_number_links[i]).attr('href', next_url);
                }
            }


        })