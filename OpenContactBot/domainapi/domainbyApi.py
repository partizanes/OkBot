import re
import requests

from config import Config as cfg

from domainapi.types.clients.searchCriterionTypes import SearchCriterionTypes
from domainapi.types.services.serviceTypes import ServiceTypes
from domainapi.types.services.serviceStatusTypes import ServiceStatusTypes
from domainapi.yandexEmails import buildYandexAliasList

from log import Log

class DomainbyApi(object):

    log = Log('DomainbyApi')
    parentUrl = cfg.getApiUrl()
    apiKey = cfg.getApiKey()
    
    @staticmethod
    def GetClients(searchCriterion: SearchCriterionTypes, searchString: str, apiKey=apiKey):

        # Build request string
        urlString = "{0}GetClients?apiKey={1}&searchCriterion={2}&searchText={3}".format(DomainbyApi.parentUrl, apiKey, searchCriterion.name, searchString)
        
        try:
            response = requests.get(urlString)

            if(response.status_code != 200): 
                raise Exception("[GetClients] Answer code {0}. urlString: {1}".format(response.status_code, urlString))

            return response.json()

        except Exception as exc:
            DomainbyApi.log.info("[GetClients] {0}".format(exc))

    @staticmethod
    def getServices(clientid: str, serviceTypes: list = [], apiKey=apiKey):

        # Build request string
        serviceTypesStr = "{0}{1}".format("&serviceTypes=", "&serviceTypes=".join(x.name for x in serviceTypes)) if len(serviceTypes) else ""
        urlString = "{0}GetServices?apiKey={1}&clientid={2}{3}".format(DomainbyApi.parentUrl, apiKey, clientid, serviceTypesStr)

        try:
            response = requests.get(urlString)

            if(response.status_code != 200):
                raise Exception("[getServices] Answer code {0}. urlString: {1}".format(response.status_code, urlString))

            return response.json()

        except Exception as exc:
            DomainbyApi.log.info("[getServices] {0}".format(exc))

    ###################################################################

    @staticmethod
    def getListofHostingServices(emailInTicket, serviceStatusTypes: ServiceStatusTypes = [ServiceStatusTypes.OK, ServiceStatusTypes.PendingDelete]):

        listOfContract = []
        virtualHostingListTemp = []

        # Build alias list for yandex emails
        listOfEmails = buildYandexAliasList(emailInTicket)

        # Get all client json object by email with alias
        for email in listOfEmails:
            clientsId = DomainbyApi.GetClients(SearchCriterionTypes.Email, email)
            _existClientId = [contract['ClientId'] for contract in listOfContract]
            listOfContract.extend([client for client in clientsId if client['ClientId'] not in _existClientId])

        for client in listOfContract:
            virtualHostingList = DomainbyApi.getServices(client['ClientId'], [ServiceTypes.VirtualHosting])

            # Add emails to hosting service 
            for virtualHosting in virtualHostingList:
                virtualHosting["UserEmail"] = client["UserEmail"]
                virtualHosting["AllEmails"] = client["AllEmails"]

                # fix ru domains 
                _domain = virtualHosting["DomainName"]
                virtualHosting["DomainName"] = _domain.encode("idna").decode("utf-8") if re.search('[а-яА-Я]', _domain) else _domain

            virtualHostingListTemp.extend([virtualHosting for virtualHosting in virtualHostingList if virtualHosting['ServiceStatus'] in [serviceStatus.name for serviceStatus in serviceStatusTypes]])

        return virtualHostingListTemp