'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  API_URL: 'http://localhost:8000',
  proxy:{
    '/api*':{
      target:'http://localhost:8000',
    }
  }

})
