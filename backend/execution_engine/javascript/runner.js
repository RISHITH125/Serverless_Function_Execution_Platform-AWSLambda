async function executeFunction(code, args) {
    let result;
    try {
        const main = new Function(...args.map((_, i) => `arg${i}`), code + '\nreturn main(...arguments);');
        result = { result: main(...args) };
    } catch (e) {
        result = { error: e.toString() };
    }
    console.log(JSON.stringify(result));
}

(async () => {
    try{
        const input = JSON.parse(process.argv[2]);
        const code = input.code;
        const args = input.args || [];
        await executeFunction(code, args);
    } catch (e) {
        console.error('Error parsing input:', e);
        console.log(JSON.stringify({ error: e.toString() }));
    }
})();
