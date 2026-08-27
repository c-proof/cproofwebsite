document.addEventListener("DOMContentLoaded", () => {
    fetch('gliderdata/deployments/active_deployments.txt')
        .then(response => response.text())
        .then(data => {
            const urls = data.split('\n').map(line => line.trim()).filter(line => line);
            const container = document.getElementById('image-container');

            if (urls.length === 0) {
                container.innerHTML = '<p>No deployments currently active</p>';
                return;
            }
            urls.forEach(url => {
                const urlparts = url.split('/');
                const glider = urlparts[0]
                const mission = urlparts[1]
                console.log('URL', glider, mission);
                url = 'gliderdata/deployments/' + url + '/figs/overview_pcolor_' + mission + '.png';
                console.log('URL', url);
                const link = document.createElement('a');
                link.href = 'gliderdata/deployments/' + glider + '/' + mission + '/'

                const imgDiv = document.createElement('div');
                imgDiv.className = 'image-item';
                const img = document.createElement('img');
                img.src = url;
                img.alt = "Image";
                link.appendChild(img);
                imgDiv.appendChild(link)
                container.appendChild(imgDiv);
            });
        })
        .catch(error => {
            console.error('Error fetching the image list:', error);
        });
});