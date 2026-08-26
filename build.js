const fs = require('fs');
const path = require('path');

function copyFolderSync(from, to) {
    if (!fs.existsSync(to)) {
        fs.mkdirSync(to, { recursive: true });
    }
    fs.readdirSync(from).forEach(element => {
        const srcPath = path.join(from, element);
        const destPath = path.join(to, element);
        const stat = fs.lstatSync(srcPath);
        if (stat.isFile()) {
            fs.copyFileSync(srcPath, destPath);
        } else if (stat.isDirectory()) {
            copyFolderSync(srcPath, destPath);
        }
    });
}

const source = path.join(__dirname, 'physio-web', 'frontend');
const destination = path.join(__dirname, 'dist');

console.log(`📦 Copying frontend files from ${source} to ${destination}...`);
copyFolderSync(source, destination);
console.log('✅ Frontend assets successfully prepared in dist/ directory for Vercel deployment!');
