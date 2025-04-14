async function executeFunction(code, args) {
  let result; const logs = []; const errors = [];

  const originalLog = console.log;
  const originalError = console.error;

  console.log = (...msgs) => logs.push(msgs.join(" "));
  console.error = (...msgs) => errors.push(msgs.join(" "));
  
  try {
    const main = new Function(
      ...args.map((_, i) => `arg${i}`),
      code + "\nreturn main(...arguments);"
    );
    const returnValue = main(...args);
    result = {
      returnValue: returnValue !== undefined ? returnValue : null,
      logs: logs.length > 0 ? logs : null,
      errors: errors.length > 0 ? errors : null,
    }

  } catch (e) {
    result = {
      error: e.toString(),
      logs,
      errors: errors.length ? errors : [e.stack],
    };
  } finally {
    console.log = originalLog;
    console.error = originalError;
  }
  originalLog(JSON.stringify(result));
}

(async () => {
  try {
    const input = JSON.parse(process.argv[2]);
    const code = input.code;
    const args = input.args || [];
    await executeFunction(code, args);
  } catch (e) {
    console.error("Error parsing input:", e);
    console.log(JSON.stringify({ error: e.toString() }));
  }
})();
