const devCerts = require("office-addin-dev-certs");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const HtmlWebpackPlugin = require("html-webpack-plugin");
const webpack = require('webpack');

module.exports = async (env, options)  => {
  const dev = options.mode === "development";
  let domain = "localhost:3000";
  if (env && env.DOMAIN) {
    domain = env.DOMAIN;
  }
  const config = {
    devtool: "source-map",
    entry: {
      vendor: [
        'react',
        'react-dom',
        'core-js',
        'office-ui-fabric-react'
    ],
    taskpane: [
        'react-hot-loader/patch',
        './src/taskpane/index.tsx',
    ],
    },
    resolve: {
      extensions: [".ts", ".tsx", ".html", ".js"]
    },
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: [
              'react-hot-loader/webpack',
              'ts-loader'
          ],
          exclude: /node_modules/
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader']
        },
        {
          test: /\.(png|jpe?g|gif|svg|woff|woff2|ttf|eot|ico)$/,
          use: {
              loader: 'file-loader',
              query: {
                  name: 'assets/[name].[ext]'
                }
              }  
            }   
          ]
    },    
    plugins: [
      new CleanWebpackPlugin(),
      new CopyWebpackPlugin(
        {
          patterns: [
            {
              to: "taskpane.css",
              from: "./src/taskpane/taskpane.css"
            },
            {
              from: './assets',
              to: 'assets',
              globOptions: {
                ignore: ['*.scss'],
              }
            },
            {
              to: "manifest.xml",
              from: "./manifest.xml",
              transform(content) {
                return content
                  .toString()
                  .replace(/localhost:3000/g, domain);
              },
            },
          ]
        }
      ),
      new webpack.DefinePlugin({
        __DOMAIN__: JSON.stringify(domain)
      }),
      new ExtractTextPlugin('[name].[hash].css'),
      new HtmlWebpackPlugin({
        filename: "taskpane.html",
          template: './src/taskpane/taskpane.html',
          chunks: ['taskpane', 'vendor', 'polyfills']
      }),
      new HtmlWebpackPlugin({
        filename: "dialog.html",
        template: "./src/taskpane/components/Login/dialog.html"
      }),
      new webpack.ProvidePlugin({
        Promise: ["es6-promise", "Promise"]
      })
    ],
    devServer: {
      headers: {
        "Access-Control-Allow-Origin": "*"
      },      
      https: (options.https !== undefined) ? options.https : await devCerts.getHttpsServerOptions(),
      port: process.env.npm_package_config_dev_server_port || 3000
    }
  };

  return config;
};
