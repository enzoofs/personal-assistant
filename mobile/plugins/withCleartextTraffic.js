const { withAndroidManifest } = require('@expo/config-plugins');

module.exports = function withCleartextTraffic(config) {
  return withAndroidManifest(config, async (config) => {
    const androidManifest = config.modResults;
    const application = androidManifest.manifest.application[0];

    // Force cleartext traffic
    application.$['android:usesCleartextTraffic'] = 'true';

    return config;
  });
};
