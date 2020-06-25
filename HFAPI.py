# PYTHON 3.7.2
# HF API V2 PYTHON WRAPPER #
# Based off Xerotic's PHP Class #

import requests
import json
class HF_API:

    client_id = None
    secret_key = None
    access_token = None
    uid = None
    errors = {}
    state = None
    redirect_uri = None
    auth_url = "https://hackforums.net/api/v2/authorize"
    read_url = "https://hackforums.net/api/v2/read"
    write_url = "https://hackforums.net/api/v2/write"

    # Constructor Method, aka: __init__() #

    def __init__(self, state=None):
        if state:
            self.setState(state)

    def setClientID(self, client_id):
        self.client_id = client_id

    def setSecretKey(self, secret_key):
        self.secret_key = secret_key

    def setRedirectUri(self, uri):
        self.redirect_uri = uri

    def getAccessToken(self):
        return self.access_token

    def setAccessToken(self, access_token):
        self.access_token = access_token

    def checkAccessToken(self):
        if self.access_token:
            return True
        else:
            return False

    def getUID(self):
        return self.uid

    def setError(self, error):
        self.errors["Error"] = error

    def getErrors(self):
        return self.errors

    def setState(self, state):
        self.state = state

    def getState(self):
        return self.state

    def sendRequest(self, url, post_fields = {}, hf_asks={}):

        
        if hf_asks:
            response = requests.post(url,
                                     data = {"asks":json.dumps(hf_asks)},
                                     headers = {"Authorization": f"Bearer {self.access_token}"}
                                     )
        if post_fields:
            response = requests.post(url,
                                     data = post_fields)
        if json.loads(response.text):
            response_dict = json.loads(response.text)
            if 'message' in response_dict.keys():
                 self.setError(response_dict["message"])
                 return self.getErrors()
            else:
                return json.loads(response.text)
        else:
            self.setError("IP BLACKLISTED")
            return self.getErrors()
            

    def startAuth(self):
        
        ## MODIFY CODE HERE: Since this is made for a web app, its returning
        ## a auth page URL. You can redirect user or make your browser open it.
        if self.client_id:
            auth_page = f"{self.auth_url}?response_type=code&client_id={self.client_id}&state={self.state}&redirect_uri={self.redirect_uri}"
            return auth_page

    def finishAuth(self, auth_code, state): # You will receive the auth_code from the paremter 'code' after user authorizes your service.
        post_fields = {'grant_type':'authorization_code',
                       'client_id':self.client_id,
                       'client_secret':self.secret_key,
                       'code':auth_code}
        response = self.sendRequest(self.auth_url, post_fields)
        self.access_token = response['access_token']
        self.uid = response['uid']

    def read(self, hf_asks):
        if not self.access_token:
            self.setError("NO ACCESS TOKEN SET")
            return self.getErrors()
        else:
            return self.sendRequest(self.read_url,{}, hf_asks)
            
    def write(self,hf_asks):
        if not self.access_token:
            self.setError("NO ACCESS TOKEN SET")
            return self.getErrors()
        else:
            return self.sendRequest(self.write_url,{}, hf_asks)

    def cleanAsks(self, hf_asks, mainKey):
        emptykey = []
        for key in hf_asks[mainKey]:
            
            if not hf_asks[mainKey][key]:
                emptykey.append(key)
        for key in emptykey:
            hf_asks[mainKey].pop(key, "")
        
        return hf_asks

    def makePost(self, tid, message):
        tid = int(tid)
        hf_asks = {"posts":{'_tid' : tid,'_message' : message}}
        return self.write(hf_asks)
        

    def makeThread(self, fid, subject, message):
        hf_asks = {"threads": {'_fid' : fid,'_subject' : subject,'_message' : message}}
        return self.write(hf_asks)

    def sendBytes(self, reciever, amount, reason=None, pid=None): # no option for reason and PID.
        hf_asks = {"bytes": {'_uid' : reciever,'_amount' : amount,'_reason':reason,'_pid':pid}}
        hf_asks = self.cleanAsks(hf_asks, "bytes")
        self.write(hf_asks)

    def deposit(self, amount):
        hf_asks = {"bytes":{'_deposit' : amount}}
        self.write(hf_asks)

    def withdraw(self, amount):
        hf_asks = {"bytes":{'_withdraw' : amount}}
        self.write(hf_asks)

    def createContract(self, uid,terms, their_product=None, their_currency=None, their_amount = None, your_product=None, your_currency=None, your_amount=None, tid=None, muid=None, timeout=None,position=None, public=None, address=None):
        hf_asks = {"contracts":{
            '_action':'new',
            '_uid':uid,
            '_theirproduct':their_product,
            '_theircurrency':their_currency,
            '_theiramount':their_amount,
            '_yourproduct':your_product,
            '_yourcurrency':your_currency,
            '_youramount':your_currency,
            '_tid':tid,
            '_muid':muid,
            '_timeout':timeout,
            '_position':position,
            '_terms':terms,
            '_public':public,
            '_address':address}}
        hf_asks = self.cleanAsks(hf_asks, "contracts")
        if not position:
            self.setError("NO POSITION SET")
            return self.getErrors()
        elif not uid:
            self.setError("NO UID SET")
            return self.getErrors()
        elif not terms:
            self.setError("NO TERMS SET")
            return self.getErrors()
        else:
            return self.write(hf_asks)

    def undoContract(self, cid):
        hf_asks = {"contracts": {'_action':"undo", '_cid':cid}}
        self.write(hf_asks)

    def denyContract(self, cid):
        hf_asks = {"contracts":{'_action':"deny", '_cid':cid}}
        self.write(hf_asks)

    def approveContract(self, cid, address=None):
        hf_asks = {"contracts":{'_action':"approve", '_cid':cid, '_address':address}}
        hf_asks = self.cleanAsks(hf_asks, "contracts")
        self.write(hf_asks)

    def mmDeny(self,cid):
        hf_asks={"contracts": {"_action":"middleman_deny", "_cid":cid}}

        self.write(hf_asks)

    def mmApprove(self, cid):
        hf_asks = {"contracts": {"_action":"middleman_approve","_cid":cid}}

        self.write(hf_asks)

    def vendorCancelContract(self, cid):
        hf_asks = {"contracts": {"_action":"vendor_cancel", "_cid":cid}}

        self.write(hf_asks)

    def cancelContract(self, cid):
        hf_asks = {"contracts" : {'_action':"cancel", '_cid':cid}}

        self.write(hf_asks)

    def completeContract(self, cid, txn=None):
        hf_asks = {"contracts" : {'_action':"complete", '_cid':cid, '_txn':txn}}
        hf_asks = self.cleanAsks(hf_asks, "contracts")
        self.write(hf_asks)

    def me(self, uid=None,vault = None, username=None, usergroup=None, displaygroup=None,additionalgroups=None,postnum=None,awards=None,byte=None,threadnum=None,avatar=None,avatardimensions=None,avatartype=None,lastvisit=None,usertitle=None,website=None,timeonline=None,reputation=None,referrals=None,lastactive=None,undreadpms=None,invisible=None,totalpms=None,warningpoints=None,):
        hf_asks={"me" : {
            'vault' :vault,
            'uid' :uid,
            'username' :username,
            'usergroup' :usergroup,
            'displaygroup' :displaygroup,
            'additionalgroups' :additionalgroups,
            'postnum' postnum,
            'awards' : awards,
            'bytes' : byte,
            'threadnum' : threadnum,
            'avatar' : avatar,
            'avatardimensions' : avatardimensions,
            'avatartype' : avatartype,
            'lastvisit' : lastvisit,
            'usertitle' : usertitle,
            'website' : website,
            'timeonline' : timeonline,
            'reputation' : reputation,
            'referrals' : referrals,
            'lastactive' : lastactive,
            'unreadpms' : unreadpms,
            'invisible' : invisible,
            'totalpms' : totalpms}}
        hf_asks=self.cleanAsks(hf_asks, "me")
        return self.read(hf_asks)

