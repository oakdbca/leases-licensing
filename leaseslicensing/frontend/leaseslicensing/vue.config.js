const path = require('path');
const webpack = require('webpack');
// Useful plugin to find out what is making the bundle so big
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const port = process.env.PORT ? parseInt(process.env.PORT) : 9072;

module.exports = {
    outputDir: path.resolve(__dirname, '../../static/leaseslicensing_vue'),
    publicPath: '/static/leaseslicensing_vue/',
    filenameHashing: false,
    chainWebpack: config => {
        config.resolve.alias.set('@vue-utils', path.resolve(__dirname, 'src/utils/vue'));
        config.resolve.alias.set('@common-utils', path.resolve(__dirname, 'src/components/common/'));
        config.resolve.alias.set('@static-root', path.resolve(__dirname, '../../../staticfiles_ll/'));
    },
    configureWebpack: {
        devtool: 'source-map',
        plugins: [
            new webpack.ProvidePlugin({
                $: 'jquery',
                moment: 'moment',
                swal: 'sweetalert2',
                _: 'lodash',
            }),
            // new BundleAnalyzerPlugin(),
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
                        filename: 'img/[name][ext]'
                    }
                },
                /* config.module.rule('fonts') */
                {
                    test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/i,
                    type: 'asset/resource',
                    generator: {
                        filename: 'fonts/[name][ext]'
                    }
                },
            ]
        },
    }
};
