import requests as req
import json
import csv
from datetime import datetime


# 1. TEAM MEMBERS
class Team:
    def getMembers(self):
        res = Http.get('https://www.streak.com/api/v2/users/me/teams')
        list = []
        for i in res['results'][0]['members']:
            if 'fullName' in i:
                name = i['fullName']
            else:
                name = i['displayName']
            list.append({'name': name,
                         'email': i['email'],
                         'key': i['userKey']})
        return list

    def getName(self, key):
        res = Team.getMembers()
        for i in res:
            if i['key'] == key:
                return i['name']
        return "No team member has that key"

    def getTeamMemberKey(self, name):
        res = Team.getMembers()
        for i in res:
            if i['name'] == name:
                return i['key']
        return "No team member has that name"


# 2. PIPELINES
class Pipe:
    def getPipelines(self):
        res = Http.get("https://www.streak.com/api/v1/pipelines")
        pipes = []
        for i in res:
            pipes.append({'name': i['name'], 'key': i['key'],
                          'creator': Team.getName(res['creatorKey']),
                          'stages': []})
            for j in i['stages'].values():
                pipes[-1]['stages'].append(j['name'])
        return pipes

    def getPipeline(self, p_name):
        p_key = Pipe.getKey(p_name)
        res = Http.get("https://www.streak.com/api/v1/pipelines/" + p_key)
        pip = {'name': p_name, 'key': p_key,
               'creator': Team.getName(res['creatorKey']), 'stages': []}
        for j in res['stages'].values():
            pip['stages'].append(j['name'])
        return pip

    def getKey(self, name):
        res = Http.get("https://www.streak.com/api/v1/pipelines")
        for i in res:
            if i['name'] == name:
                return i['pipelineKey']

    def getPipeName(self, key):
        res = Http.get("https://www.streak.com/api/v1/pipelines")
        for i in res:
            if i['pipelineKey'] == key:
                return i['name']


# 3. BOXES
class Box:
    def getBoxes(self, p_name, fields={}, s_name=''):
        """
        Retrieves the given fields of all the boxes in that stage
        @param pipe_name: String
        @param stage_name: String
        @param fields: Dict.: Desired name references real name.
        If function should be applied:
            'desiredName': ['realName', '', 'funcName']
            u_name: user (get name from team member with key)
            t_name: time (get date with timestamp)
            s_name: stage (get name with key and pipeline)
            au_name: array of team members (get names)
            af_name: get value of field[arr, key]
            ao_name: get names of organizations
        @return out: list of dicts
        """
        res = Http.get("https://www.streak.com/api/v1/pipelines/" +
                       Pipe.getKey(p_name) + "/boxes")
        if not fields:
            return res
        out = []
        for i in res:
            if s_name != '':
                if Stage.getName(p_name, i['stageKey']) != s_name:
                    continue
            out.append({})
            for key in fields:
                if key[:2] == 'u_':
                    out[-1][key[2:]] = Team.getName(i[fields[key]])
                elif key[:2] == 't_':
                    out[-1][key[2:]] = Time.getUTC(i[fields[key]])
                elif key[:2] == 's_':
                    out[-1][key[2:]] = Stage.getName(p_name, i[fields[key]])
                elif key[:3] == 'au_':
                    arr = []
                    for j in i[fields[key]]:
                        try:
                            arr.append(j['fullName'])
                        except KeyError:
                            arr.append(j['displayName'])
                    out[-1][key[3:]] = arr
                elif key[:3] == 'af_':
                    try:
                        out[-1][key[3:]] = i[fields[key][0]][fields[key][1]]
                    except KeyError:
                        out[-1][key[3:]] = ''
                elif key[:3] == 'ao_':
                    arr = []
                    if 'organizations' in i:
                        for x in i[fields[key]]:
                            arr.append(Org.getName(x['key']))
                        out[-1][key[3:]] = arr
                    else:
                        out[-1][key[3:]] = ''

                else:
                    out[-1][key] = i[fields[key]]
        return out

    def getBox(self, box_key):
        res = Http.get("https://www.streak.com/api/v1/boxes/" + box_key)
        return {'name': res['name'],
                'stage': Stage.getName(Pipe.getName(res['pipelineKey']),
                                       res['stageKey']),
                'creator': Team.getName(res['creatorKey']),
                'creation': Time.getUTC(res['creationTimestamp']),
                'pipeline': Pipe.getName(res['pipelineKey'])}

    def getName(self, box_key):
        return Box.getBox(box_key)['name']

    def getKey(self, pipe_name, box_name):
        res = Box.getBoxes(pipe_name)
        for i in res:
            if i['name'] == box_name:
                return i['key']

    def delete(self, box_key):
        Http.delete("https://www.streak.com/api/v1/boxes/" + box_key)

    def saveBoxes(self, boxes, file, p_name, s_name):
        boxes = Box.formatBoxes(boxes)
        if file == '':
            date = Time.getActualFormattedDate()
            file = date + "_" + p_name + "_" + s_name + ".csv"
            with open(file, 'w', newline='') as file:
                w = csv.DictWriter(file, fieldnames=boxes[0].keys())
                w.writeheader()
                for i in boxes:
                    w.writerow(i)
        else:
            with open(file, 'a', newline='') as file:
                w = csv.DictWriter(file, fieldnames=boxes[0].keys())
                for i in boxes:
                    w.writerow(i)

    def formatBoxes(self, boxes):
        """
        Substitute arrays with strings of elements
        """
        for i in boxes:
            for key in i:
                if type(i[key]) == list:
                    str = ""
                    for j in i[key]:
                        str += j + ", "
                    i[key] = str[:-2]
        return boxes


# 4. USERS
class User:
    def getUser(self, key):
        res = Http.get("https://www.streak.com/api/v1/users/" + key)
        usr = {}
        if 'googleProfileFullName' in res:
            usr['name'] = res['googleProfileFullName']
        usr['email'] = res['email']
        return usr

    def getName(self, key):
        return User.getUser(key)['name']


# 5. ORGANIZATIONS
class Org:
    def getName(self, org_key):
        return Http.get('https://www.streak.com/api/v2/organizations/' +
                        org_key)['name']


# 6. STAGES
class Stage:
    def getName(self, p_name, s_key):
        return Http.get("https://www.streak.com/api/v1/pipelines/" +
                        Pipe.getKey(p_name) + "/stages/" + s_key)['name']

    def getKey(self, pipe_name, stage_name):
        return Pipe.getPipeline(pipe_name)['stages'].index(stage_name) + 5001


# 7. HTTP
class Http:
    def get(self, url):
        key = '4e25a78734d34b2e9229cd5086f1fa7f'
        return json.loads(req.get(url, auth=(key, '')).text)

    def delete(self, url):
        key = '4e25a78734d34b2e9229cd5086f1fa7f'
        req.delete(url, auth=(key, ''))


# 8. TIME
class Time:
    def getUTC(self, ts):
        return datetime.utcfromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S')

    def getActualFormattedDate(self):
        now = datetime.now()
        return str(now.year) + str(now.month) + str(now.day)


# 9. COMMENT
class Comment:
    def get(b_key, fields={}):
        """
        Retrieves the given fields of all the comments in that box
        @param b_key: String: key of the box
        @param fields: Dict.: Desired name references real name.
        If function should be applied:
            'desiredName': ['realName', '', 'funcName']
            u_name: user (get name from team member with key)
            t_name: time (get date with timestamp)
            au_name: array of team members (get names)
            af_name: get value of field[arr, key]
        @return out: list of dicts
        """
        res = Http.get('https://www.streak.com/api/v2/boxes/' + b_key +
                       '/comments')['results']
        if not fields:
            return res
        out = []
        for i in res:
            out.append({})
            for key in fields:
                if key[:2] == 'u_':
                    out[-1][key[2:]] = Team.getName(i[fields[key]])
                elif key[:2] == 't_':
                    out[-1][key[2:]] = Time.getUTC(i[fields[key]])
                elif key[:3] == 'au_':
                    arr = []
                    for j in i[fields[key]]:
                        if 'fullName' in j:
                            arr.append(j['fullName'])
                        else:
                            arr.append(j['displayName'])
                    out[-1][key[3:]] = arr
                elif key[:3] == 'af_':
                    if fields[key][1] in i[fields[key][0]]:
                        out[-1][key[3:]] = i[fields[key][0]][fields[key][1]]
                    else:
                        out[-1][key[3:]] = ''
                else:
                    out[-1][key] = i[fields[key]]
        return out

    def save(coms, p_name, b_name):
        file = b_name + "_" + p_name + ".csv"
        with open(file, 'w', newline='') as file:
            w = csv.DictWriter(file, fieldnames=coms[0].keys())
            w.writeheader()
            for i in coms:
                w.writerow(i)


# 10. SAVE AND DELETE
class Save:
    def boxes(p_name, s_name, fields={}, file='', com_fields={}):
        """
        Get resolved boxes, save them in a sheet and delete them
        from the pipeline, after retrieving and saving their comments.
        """
        boxes = Box.getBoxes(p_name, fields, s_name)
        print(boxes)
        Box.saveBoxes(boxes, file, p_name, s_name,)
        for i in boxes:
            coms = Comment.get(i['key'], com_fields)
            Comment.save(coms, p_name, i['name'])
            Box.delete(i['key'])


if __name__ == "__main__":
    tickets_fields = {'name': 'name', 't_created': 'creationTimestamp',
                      't_lastStageChange': 'lastStageChangeTimestamp',
                      'u_creator': 'creatorKey', 's_stage': 'stageKey',
                      'au_assignedTo': 'assignedToSharingEntries',
                      'af_issue': ['fields', '1003'], 'key': 'key'}
    com_fields = {'message': 'message', 'u_creator': 'creatorKey',
                  't_created': 'timestamp'}
    sales_fields = {'name': 'name', 'af_offer': ['fields', '1004'],
                    't_created': 'creationTimestamp', 's_stage': 'stageKey',
                    't_lastStageChange': 'lastStageChangeTimestamp',
                    'au_assignedTo': 'assignedToSharingEntries',
                    'ao_organizations': 'organizations',
                    'u_creator': 'creatorKey', 'key': 'key'}

    Save.boxes('Sales Deals', 'Lead', sales_fields)
