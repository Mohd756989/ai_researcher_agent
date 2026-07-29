async function getEditContext() {
    for(let i = 0; i < 10; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    const context = {
        "filePath": "researcher_agent/program.py",
    }
}