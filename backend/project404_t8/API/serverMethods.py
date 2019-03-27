from .models import Server
from users.models import CustomUser
import requests


def get_server_info(remote_server_host):
    try:
        queryset = Server.objects.all()
        for server in queryset:
            if server.host = remote_server_host:
                return server
        return None
    except:
        return None


def get_remote_author(remote_server, remote_author_id):
    request_url = remote_server.host + "/author/" + str(remote_author_id)
    r = requests.get(request_url, auth=(remote_server.username, remote_server.password))
    if r.status_code == 200:
        response = r.text
        remote_author = CustomUser(id=remote_author_id, host=remote_server.host, \
            displayname=response.displayName, github=response.github, username = "...", \
            password= "12345", bio= "..." \
            response.bio)
        remote_author.save()
        return remote_author
    else:
        return None


def get_user(remote_author_id):
    # search for any local authors with the username
    try:
        queryset = CustomUser.objects.filter(pk=remote_author_id)
        author = UserSerializer(queryset, many=True).data[0]
        return author

    # search for any server authors with the username
    except:
        queryset = Server.objects.all()
        for server in queryset:
            author = get_remote_author(server, remote_author_id)
            if author = None:
                return None
            else:
                return author
    return None


# we send friend request to a remote server
# returns False if the operation fails
def befriend_remote_author(remote_author_id, local_author_id):

    remote_author = get_user(remote_author_id)
    if remote_author = None:
        return False # return a False if it fails
    friend = {}
    friend["id"] = local_author.id
    friend["host"] = local_author.host
    friend["displayName"] = local_author.displayname
    friend["url"] = local_author.url

    local_author = get_user(local_author_id)
    if local_author = None:
        return False
    author = {}
    author["id"] = local_author.id
    author["host"] = local_author.host
    author["displayName"] = local_author.displayname
    author["url"] = local_author.url

    data = {}
    data["query"] = "friendrequest"
    data["author"] = author
    data["friend"] = friend

    request_url = remote_server.host + "/author/" + str(remote_author_id)
    r = requests.post(request_url, auth=(remote_server.username, remote_server.password))
    response = r.text

    if r.status_code != 200:
        return False

    return True