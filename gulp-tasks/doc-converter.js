let gulp = require('gulp');
let cp = require('child_process');
let path = require('path');
let clean = require('gulp-clean');
let del = require('del')
let vinylpaths = require('vinyl-paths')

const workingDirectory = path.join(__dirname, '..', 'load-files');
const scriptfile = path.join(workingDirectory, "reload.sh");
const ProjectRoot = process.env.ProjectRoot;
const DocConverterServer = process.env.DocConverterServer;
const DocConverterPort = process.env.DocConverterPort;
const dcbaseDir = path.join(__dirname, '..');
const dck8sDir = path.join(dcbaseDir, '..', 'k8s', 'config', 'doc-converter')

function execute(command, callback){
    return cp.exec(command, function(error, stdout, stderr){ callback(stdout); });
};


gulp.task('doc-converter-clean-working-files', (done) => {
    try {
        gulp.src(['./doc_converter/app/upload/*.*', './doc_converter/app/download/*.*', './doc_converter/app/log/*.*'], {allowEmpty: true})
            .pipe(vinylpaths(del));
    }  
    catch (e) {}
    done();
});

gulp.task('doc-converter-container-launch', gulp.series(
    'doc-converter-clean-working-files',
    (done) => {
        console.log("Working Directory:" + workingDirectory)
        const buildSubprocess = cp.spawnSync(scriptfile, {
            cwd:workingDirectory,
            stdio: [0, 1, 2], 
            env: process.env
    });
    done();
}));

// for testing file conversion:
//curl -F file=@$ProjectRoot/test/doc_converter_test/test-files/processmgr-pptx-svg.pptx http://localhost:5002/svgconvert



gulp.task('doc-converter-send-post', (done) => {
    var sendfile = ProjectRoot + "/test/doc_converter_test/test-files/processmgr-pptx-svg.pptx";
    var url = "http://" + DocConverterServer + ":" + DocConverterPort + "/svgconvert";
    var curlcommand = "curl -F file=@" + sendfile + " " + url;
    console.log("sending commmand: " + curlcommand);
    execute(curlcommand, console.log);
    done();
});

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

gulp.task('test-container-build-doc-converter', gulp.series(['doc-converter-container-launch', 'sleep-2','container-test-doc-converter','container-stop-doc-converter']))


const dcprocessConfig = {
    cwd: dcbaseDir,
    stdio: [0,1,2],
    env: process.env
};

const dck8sProcessConfig = {
    cwd: dck8sDir,
    stdio: [0,1,2],
    env: process.env
};

gulp.task('doc-converter-update-requirements', async () => {
    cp.execSync(". venv/bin/activate && pip freeze > requirements.txt", dcprocessConfig)
});


gulp.task('doc-converter-docker-build', async () => {
    cp.execSync("docker build . -t khannegan/chart-a-lot:doc-converter --network=host --no-cache", dcprocessConfig)
});

gulp.task('doc-converter-docker-push', async () => {
    cp.execSync("docker push khannegan/chart-a-lot:doc-converter", dcprocessConfig)
});

gulp.task('doc-converter-k8s-update-config', async ()=> {
    cp.execSync("kubectl apply -f .", dck8sProcessConfig)
});

gulp.task('doc-converter-k8s-delete-pod', async ()=> {
    cp.execSync("kubectl delete pod -n api -l app=doc-converter", dck8sProcessConfig)
});

gulp.task('doc-converter-redeploy',
    gulp.series(
        'doc-converter-update-requirements',
        'doc-converter-docker-build',
        'doc-converter-docker-push',
        'doc-converter-k8s-update-config',
        'doc-converter-k8s-delete-pod'
    )
);