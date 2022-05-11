const nacl = require("tweetnacl")
const axios = require("axios");
const Base64 = require("js-base64");
nacl.util = require('tweetnacl-util');

const textDecoder = new TextDecoder();

var password = "Yellow_Submarine"

axios({
  url: "http://columbus-config-qa02.s3-website-us-west-1.amazonaws.com",
  method: "get",
}).then((res) => {
  // console.log(res.data)
  const nonce = Base64.toUint8Array(res.data.nonce);
  const message = Base64.toUint8Array(res.data.payload);
  const box = nacl.secretbox.open(message, nonce, nacl.util.decodeUTF8(password.padStart(32, '0')));
  console.log(textDecoder.decode(box))

}).catch((error) => {
  console.log(error);
})