const path = require('path');
const webpack = require('webpack');
const MomentLocalesPlugin = require('moment-locales-webpack-plugin');
const {
    CKEditorTranslationsPlugin,
} = require('@ckeditor/ckeditor5-dev-translations');
const { styles } = require('@ckeditor/ckeditor5-dev-utils');

// Useful plugin to find out what is making the bundle so big
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const port = process.env.PORT ? parseInt(process.env.PORT) : 9072;
const webpack_devtool = process.env.WEBPACK_DEVTOOL || 'source-map';

module.exports = {
    outputDir: path.resolve(__dirname, '../../static/leaseslicensing_vue'),
    publicPath: '/static/leaseslicensing_vue/',
    filenameHashing: false,
    chainWebpack: (config) => {
        config.resolve.alias.set(
            '@vue-utils',
            path.resolve(__dirname, 'src/utils/vue')
        );
        config.resolve.alias.set(
            '@common-utils',
            path.resolve(__dirname, 'src/components/common/')
        );
        config.resolve.alias.set(
            '@static-root',
            path.resolve(__dirname, '../../../staticfiles_ll/')
        );

        // https://ckeditor.com/docs/ckeditor5/latest/installation/integrations/vuejs-v3.html#webpack
        // (1.) To handle the editor icons, get the default rule for *.svg files first:
        const svgRule = config.module.rule('svg');

        // Then you can either:
        //
        // * clear all loaders for existing 'svg' rule:
        //
        //		svgRule.uses.clear();
        //
        // * or exclude ckeditor directory from node_modules:
        svgRule.exclude.add(path.join(__dirname, 'node_modules', '@ckeditor'));

        // Add an entry for *.svg files belonging to CKEditor. You can either:
        //
        // * modify the existing 'svg' rule:
        //
        //		svgRule.use( 'raw-loader' ).loader( 'raw-loader' );
        //
        // * or add a new one:
        config.module
            .rule('cke-svg')
            .test(/ckeditor5-[^/\\]+[/\\]theme[/\\]icons[/\\][^/\\]+\.svg$/)
            .use('raw-loader')
            .loader('raw-loader');

        // (2.) Transpile the .css files imported by the editor using PostCSS.
        // Make sure only the CSS belonging to ckeditor5-* packages is processed this way.
        config.module
            .rule('cke-css')
            .test(/ckeditor5-[^/\\]+[/\\].+\.css$/)
            .use('postcss-loader')
            .loader('postcss-loader')
            .tap(() => {
                return {
                    postcssOptions: styles.getPostCssConfig({
                        themeImporter: {
                            themePath: require.resolve(
                                '@ckeditor/ckeditor5-theme-lark'
                            ),
                        },
                        minify: true,
                    }),
                };
            });
    },
    transpileDependencies: [/ckeditor5-[^/\\]+[/\\]src[/\\].+\.js$/],
    configureWebpack: {
        devtool: webpack_devtool,
        plugins: [
            new webpack.DefinePlugin({
                // Vue CLI is in maintenance mode, and probably won't merge my PR to fix this in their tooling
                // https://github.com/vuejs/vue-cli/pull/7443
                __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
            }),
            new webpack.ProvidePlugin({
                $: 'jquery',
                moment: 'moment',
                swal: 'sweetalert2',
                _: 'lodash',
            }),
            new MomentLocalesPlugin(),
            // new BundleAnalyzerPlugin(),
            // CKEditor 5 needs its own plugin to be built using webpack.
            new CKEditorTranslationsPlugin({
                // See https://ckeditor.com/docs/ckeditor5/latest/features/ui-language.html
                language: 'en',

                // Append translations to the file matching the `app` name.
                translationsOutputFile: /app/,
            }),
        ],
        devServer: {
            host: '0.0.0.0',
            allowedHosts: 'all',
            devMiddleware: {
                //index: true,
                writeToDisk: true,
            },
            client: {
                webSocketURL: 'ws://0.0.0.0:' + port + '/ws',
            },
        },
        module: {
            rules: [
                /* config.module.rule('images') */
                {
                    test: /\.(png|jpe?g|gif|webp|avif)(\?.*)?$/,
                    type: 'asset/resource',
                    generator: {
                        filename: 'img/[name][ext]',
                    },
                },
                /* config.module.rule('fonts') */
                {
                    test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/i,
                    type: 'asset/resource',
                    generator: {
                        filename: 'fonts/[name][ext]',
                    },
                },
            ],
        },
        performance: {
            hints: false,
        },
    },
};
