let gulp = require('gulp');
let cp = require('child_process');
let path = require('path');

const workingDirectory = path.join(__dirname, '..', 'load-files');
const scriptfile = path.join(workingDirectory, "reload.sh")


gulp.task('container-launch-doc-converter', (done) => {
    console.log("Working Directory:" + workingDirectory)
    const buildSubprocess = cp.spawnSync(scriptfile, {
        cwd:workingDirectory,
        stdio: [0, 1, 2], 
        env: process.env
    });
    done();
});

function execute(command, callback){
    return cp.exec(command, function(error, stdout, stderr){ callback(stdout); });
};

function allTasksRunning(lines) {
    var statusArray = lines.split(/\r?\n/);
    var message = "";
    var isWorking = true
    statusArray.forEach(element => {
        if (element != "RUNNING" && element != "")
        {
            isWorking = false;
        }
    });
    if (isWorking)
    {
        console.log("Container Build Successful");
    }
    else
    {
        console.log("WARNING!!! Container subprocesses failed to load.  Please review and debug dockerfile.  WARNING!!!");
        throw Error("Container build unsuccessful.");
    };
};


gulp.task('container-test-doc-converter', () => {
    console.log("2 sec sleep gives container time to initialize");
    return execute("docker exec -t doc_converter supervisorctl status all | awk '{print $2}'", allTasksRunning);
});

gulp.task('container-stop-doc-converter', () => {
    return cp.exec("docker container stop doc_converter");
});

gulp.task('test-container-build-doc-converter', gulp.series(['container-launch-doc-converter', 'sleep-2','container-test-doc-converter','container-stop-doc-converter']))