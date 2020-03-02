const fs = require('fs');
const electron = require("electron");
const url = require("url");
const path = require("path");
const { default: SlippiGame } = require('slp-parser-js');
const {spawn} = require('child_process');


//for retreiving asar archive python script
// const originalFs = require('original-fs');
// console.log(originalFs.readdirSync('python'))


//electron stuff
const {app, BrowserWindow, Menu, ipcMain} = electron;
const dialog = electron.dialog


let mainWindow;


// Listen for app to be ready
app.on('ready', function(){
    //create new window
    mainWindow = new BrowserWindow({
        width: 700,
        height: 410,
        webPreferences: {
            nodeIntegration: true,
            disableHtmlFullscreenWindowResize: true
        },
        autoHideMenuBar: true,
        // frame: false,
        resizable: false,
        // titleBarStyle: "hidden"
        icon: __dirname + "/assets/icons/png/icon.png"
        
    })


    mainWindow.fullScreenable = false;
    //load html into window
    mainWindow.loadURL(url.format({
        pathname: path.join(__dirname, "index.html"),
        protocol:"file:",
        slashes:true
    }))


});

app.on('window-all-closed', () => {
    // On macOS it is common for applications and their menu bar
    // to stay active until the user quits explicitly with Cmd + Q
    if (process.platform !== 'darwin') {
      app.quit()
    }
  })

var folderUrl;

//
ipcMain.on('run', function(e, item){
    console.log(folderUrl)
    console.log(item);
    if (folderUrl == undefined){
        e.reply("selectAPath");
        return;
    }
    writePorts(item, folderUrl, e, callback);
})

function callback(folderUrl, e, filesLength){
    console.log("Created slippinames.json file, now running analyzer");
    runSlippiAnalyzer(folderUrl, e, filesLength);
}

ipcMain.on("openDialog", function(e){
    // console.log(item);
    dialog.showOpenDialog({
        properties: ['openDirectory']
    }).then(result => {
        if (!result.canceled && result.filePaths != null){
            console.log(result.canceled);
            console.log(result.filePaths);
            //set filepath to global variable
            folderUrl = result.filePaths[0];
        }
    }).catch(err => {
        console.log(err)
    })
})



//slippi stuff

async function runScript(arg){
    return await spawn('python', [
        "-u",
        __dirname + "/python/slippigameanalyzer.py",
        arg
    ]);
}
async function runSlippiAnalyzer(arg, e, filesLength){
    const subprocess = spawn('python', ['-u', __dirname + "/python/slippigameanalyzer.py", arg])
    subprocess.stdout.on('data', (data) => {
        console.log(`data:${data}`);
        try{
            if (data.toString() == "DONE\r\n"){ //python print has \r\n at the end
                e.reply("done")
            } else {
                parsedData = JSON.parse(data);
                parsedData.push(filesLength); //[1, 4, 2, 3, 4, 5, 2]
                e.reply("loading", parsedData[6]/filesLength)
                e.reply("data", parsedData)
            }
        }
        catch {
            // continue;
        }
    });
    subprocess.stderr.on('data', (data) => {
        console.log(`error:${data}`);
    });
    subprocess.stderr.on('close', () => {
        console.log("Closed");
        app.quit()
    });
}
var data = [];

function writePorts(username, folderUrl, e, callback) {
    fs.readdir(folderUrl, function(err, files){
        if (!err){
            for (i = 0; i < files.length; i++){ //have some loading bar
                e.reply("loadingPort", i/files.length)
                game = new SlippiGame(folderUrl+"/"+files[i]);
                try{
                    metadata = game.getMetadata();
                }
                catch{ //not a valid .slp file
                    e.reply("selectAPath");
                    return;
                }
                // console.log(metadata.players[0])
                // console.log(metadata.players[1].names.netplay)
                for (j = 0; j < 4; j++){
                    try{
                        if (metadata.players[j].names.netplay == username){ //if found me
                            // console.log("i got you!")
                            data.push({ //add me to list
                                filename: files[i],
                                myport: j,
                            });
                            // continue;
                        }
                    } catch(TypeError) { //if outside of port range
                        // continue;
                    }
                };
            }
        // If no ports found with that username...
        if (data.length == 0){
            // Restart index to beginning
            return;
        }
        // Write to a new file
        fs.writeFile(__dirname + '/python/slippinames.json', JSON.stringify(data), (err) => {
            // Throws an error, you could also catch it here
            if (err) throw err;
            
            // Success case, the file was saved
            e.reply("loadingPort", 100)
            console.log('data saved!');
            callback(folderUrl, e, files.length);
        });
        } else { console.log(err) }
    })
}
