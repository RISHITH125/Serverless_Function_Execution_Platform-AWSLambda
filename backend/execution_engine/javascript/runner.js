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
    };
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
    let input;

    // Prefer CLI arg if it exists
    if (process.argv[2]) {
      input = process.argv[2];
    } else {
      // Fallback to stdin
      input = '';
      for await (const chunk of process.stdin) {
        input += chunk;
      }
    }

    if (!input.trim()) throw new Error("No input provided");

    const parsed = JSON.parse(input);
    const code = parsed.code;
    const args = parsed.args || [];

    await executeFunction(code, args);
  } catch (e) {
    console.error("Error parsing input:", e);
    console.log(JSON.stringify({ error: e.toString() }));
  }
})();
