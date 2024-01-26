import http from 'k6/http';
import { sleep, check, fail } from 'k6';


export let options = {
  vus: 10,
  duration: "5s",
  discardResponseBodies: true,
};


const test = async () => {
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  const url1 = 'http://0.0.0.0/book/1162241632-9791162241639/';
  const res1 = await http.get(url1, params);
  const checkResult1 = check(res1, {
    'is status 200': (r) => r.status === 200,
  });
  if (!checkResult1) {
    fail('Failed due to an unexpected status code: ' + res1.status);
  }
  sleep(10);
}

export default test;