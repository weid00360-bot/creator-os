import { Config } from '@remotion/cli/config';

Config.setEntryPoint('./src/index.js');
Config.setVideoImageFormat('jpeg');
Config.overrideWebpackConfig((config) => config);
