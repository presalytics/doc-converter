let gulp = require('gulp');
let cp = require('child_process');
let path = require('path');

const workingDirectory = path.join(__dirname, '..');
const scriptfile = path.join(workingDirectory, "reload.sh")

gulp.task('launch-doc-converter', (done) => {
    console.log("Working Directory:" + workingDirectory)
    const buildSubprocess = cp.spawn(scriptfile, {
        cwd:workingDirectory,
        stdio: [0, 1, 2], 
        env: process.env
    });
    done();
});
