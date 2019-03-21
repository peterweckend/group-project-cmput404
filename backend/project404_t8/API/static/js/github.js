function getGithubStream(url) 
{
    return fetch(url, {
        method: "GET", 
        mode: "cors", 
        cache: "no-cache", 
        credentials: "same-origin", 
        headers: {
            "Content-Type": "application/json",
            "Accept": 'application/json'
        },
        redirect: "follow", 
        referrer: "no-referrer", 
    })
    .then(response=>response.json());
}