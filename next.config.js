const webpack = require("webpack");
const CopywebpackPlugin = require("copy-webpack-plugin");
const path = require("path");

/** @type {import('next').NextConfig} */
module.exports = {
  reactStrictMode: true,
  webpack: (config) => {
    config.plugins.push(
      new webpack.DefinePlugin({
        CESIUM_BASE_URL: JSON.stringify("cesium"),
      })
    );
    config.plugins.push(
      // Copy Cesium Assets, Widgets, and Workers to a static directory
      new CopywebpackPlugin({
        patterns: [
          {
            from: path.join(__dirname, "node_modules/cesium/Build/Cesium"),
            to: path.join(__dirname, "public/cesium"),
          },
        ],
      })
    );
    config.resolve.alias.cesium = path.resolve(
      __dirname,
      "node_modules/cesium/Build/Cesium/Cesium.js"
    );
    config.amd = { toUrlUndefined: true };
    return config;
  },
};
