from lxml import etree
from xbrl_fundamentals import FundamentantalAccountingConcepts
import re
import logging


class XBRL:
    def __init__(self, XBRLInstanceLocation='/home/luke/research/sec/pysec/data/30305/dco-20121231.xml'):

        self.XBRLInstanceLocation = XBRLInstanceLocation
        self.ns = None
        self.fields = {}

        self.EntireInstanceDocument = open(XBRLInstanceLocation, 'r').read()
        self.oInstance = etree.fromstring(self.EntireInstanceDocument)

        self.GetBaseInformation()
        self.loadYear(0)

    def loadYear(self, yearminus=0):
        currentEnd = self.getNode("//dei:DocumentPeriodEndDate").text
        asdate = re.match('\s*(\d{4})-(\d{2})-(\d{2})\s*', currentEnd)
        if asdate:
            year = int(asdate.groups()[0]) - yearminus
            thisend = '%s-%s-%s' % (
                year, asdate.groups()[1], asdate.groups()[2])
            self.GetCurrentPeriodAndContextInformation(thisend)
            FundamentantalAccountingConcepts(self)
            return True
        else:
            Logger.warning(currentEnd, ' is not a date')
            return False

    def getNodeList(self, xpath, root=None):
        if not root is not None:
            root = self.oInstance
        oNodelist = root.xpath(xpath, namespaces=self.ns)
        return oNodelist

    def getNode(self, xpath, root=None):
        oNodelist = self.getNodeList(xpath, root)
        if len(oNodelist):
            return oNodelist[0]
        return None

    def GetFactValue(self, SeekConcept, ConceptPeriodType):

        factValue = None

        if ConceptPeriodType == "Instant":
            ContextReference = self.fields['ContextForInstants']
        elif ConceptPeriodType == "Duration":
            ContextReference = self.fields['ContextForDurations']
        else:
            # An error occured
            return "CONTEXT ERROR"

        if not ContextReference:
            return None

        oNode = self.getNode(
            "//" + SeekConcept + "[@contextRef='" + ContextReference + "']")
        if oNode is not None:
            factValue = oNode.text
            if 'nil' in oNode.keys() and oNode.get('nil') == 'true':
                factValue = 0
                # set the value to ZERO if it is nil
            # if type(factValue)==str:
            try:
                factValue = float(factValue)
            except:
                Logger.warning('couldnt convert %s=%s to string' % (SeekConcept, factValue))
                factValue = None
                pass

        return factValue

    def GetBaseInformation(self):
        # This gets the taxonomy version and figures out the contexts of the
        # current period (instant and dutation)

        # This differentiates between the 2009, 2011, and 2012 US GAAP
        # taxonomies...

        # US GAAP Taxonomy
        if "http://fasb.org/us-gaap/2012-01-31" in self.EntireInstanceDocument or "http://xbrl.us/us-gaap/2012-01-31" in self.EntireInstanceDocument:
            # This IS the 2012 US GAAP taxonomy
            self.fields[
                'USGAAP_TaxonomyVersion'] = "http://fasb.org/us-gaap/2012-01-31"
            self.fields[
                'Invest_TaxonomyVersion'] = "http://xbrl.sec.gov/invest/2012-01-31"
        elif "http://fasb.org/us-gaap/2011-01-31" in self.EntireInstanceDocument or "http://xbrl.us/us-gaap/2011-01-31" in self.EntireInstanceDocument:
            # This IS the 2011 US GAAP taxonomy
            self.fields[
                'USGAAP_TaxonomyVersion'] = "http://fasb.org/us-gaap/2011-01-31"
            self.fields[
                'Invest_TaxonomyVersion'] = "http://xbrl.sec.gov/invest/2011-01-31"
        elif "http://fasb.org/us-gaap/2009-01-31" in self.EntireInstanceDocument or "http://xbrl.us/us-gaap/2010-01-31" in self.EntireInstanceDocument:
            # This IS the 2009 US GAAP taxonomy
            self.fields[
                'USGAAP_TaxonomyVersion'] = "http://xbrl.us/us-gaap/2009-01-31"
            self.fields[
                'Invest_TaxonomyVersion'] = "http://xbrl.us/invest/2019-01-31"
        #"http://fasb.org/us-gaap/2009-01-31" in self.EntireInstanceDocument or "http://xbrl.us/us-gaap/2009-01-31"  in self.EntireInstanceDocument:
        else:
            # This IS the 2009 US GAAP taxonomy
            self.fields[
                'USGAAP_TaxonomyVersion'] = "http://xbrl.us/us-gaap/2009-01-31"
            self.fields[
                'Invest_TaxonomyVersion'] = "http://xbrl.us/invest/2019-01-31"

        # DEI Taxonomy
        if "http://xbrl.sec.gov/dei/2012-01-31" in self.EntireInstanceDocument:
            # This IS the 2012 DEI taxonomy
            self.fields[
                'DEI_TaxonomyVersion'] = "http://xbrl.sec.gov/dei/2012-01-31"
        elif "http://xbrl.sec.gov/dei/2011-01-31" in self.EntireInstanceDocument:
            # This IS the 2011 DEI taxonomy
            self.fields[
                'DEI_TaxonomyVersion'] = "http://xbrl.sec.gov/dei/2011-01-31"
        # "http://xbrl.sec.gov/dei/2009-01-31" in self.EntireInstanceDocument:
        else:
            # This IS the 2009 DEI taxonomy
            self.fields[
                'DEI_TaxonomyVersion'] = "http://xbrl.us/dei/2009-01-31"

        self.ns = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                   'xbrli': 'http://www.xbrl.org/2003/instance',
                   'xmlns': 'http://www.xbrl.org/2003/instance',
                   'xbrldi': 'http://xbrl.org/2006/xbrldi',
                   'us-gaap': self.fields['USGAAP_TaxonomyVersion'],
                   'dei': self.fields['DEI_TaxonomyVersion'],
                   'currency': 'http://xbrl.sec.gov/currency/2012-01-31',
                   'invest': self.fields['Invest_TaxonomyVersion']}

        # Registered Name
        oNode = self.getNode("//dei:EntityRegistrantName[@contextRef]")
        if oNode is not None:
            self.fields['EntityRegistrantName'] = oNode.text
        else:
            self.fields['EntityRegistrantName'] = "Registered name not found"

        # Fiscal year
        oNode = self.getNode("//dei:CurrentFiscalYearEndDate[@contextRef]")
        if oNode is not None:
            self.fields['FiscalYear'] = oNode.text
        else:
            self.fields['FiscalYear'] = "Fiscal year not found"

        # EntityCentralIndexKey
        oNode = self.getNode("//dei:EntityCentralIndexKey[@contextRef]")
        if oNode is not None:
            self.fields['EntityCentralIndexKey'] = oNode.text
        else:
            self.fields['EntityCentralIndexKey'] = "CIK not found"

        # EntityFilerCategory
        oNode = self.getNode("//dei:EntityFilerCategory[@contextRef]")
        if oNode is not None:
            self.fields['EntityFilerCategory'] = oNode.text
        else:
            self.fields['EntityFilerCategory'] = "Filer category not found"

        # TradingSymbol
        oNode = self.getNode("//dei:TradingSymbol[@contextRef]")
        if oNode is not None:
            self.fields['TradingSymbol'] = oNode.text
        else:
            self.fields['TradingSymbol'] = "Not provided"

        # DocumentFiscalYearFocus
        oNode = self.getNode("//dei:DocumentFiscalYearFocus[@contextRef]")
        if oNode is not None:
            self.fields['DocumentFiscalYearFocus'] = oNode.text
        else:
            self.fields[
                'DocumentFiscalYearFocus'] = "Fiscal year focus not found"

        # DocumentFiscalPeriodFocus
        oNode = self.getNode("//dei:DocumentFiscalPeriodFocus[@contextRef]")
        if oNode is not None:
            self.fields['DocumentFiscalPeriodFocus'] = oNode.text
        else:
            self.fields[
                'DocumentFiscalPeriodFocus'] = "Fiscal period focus not found"

        # DocumentType
        oNode = self.getNode("//dei:DocumentType[@contextRef]")
        if oNode is not None:
            self.fields['DocumentType'] = oNode.text
        else:
            self.fields['DocumentType'] = "Fiscal period focus not found"

    def GetCurrentPeriodAndContextInformation(self, EndDate):
        # Figures out the current period and contexts for the current period
        # instance/duration contexts

        self.fields['BalanceSheetDate'] = "ERROR"
        self.fields['IncomeStatementPeriodYTD'] = "ERROR"

        self.fields['ContextForInstants'] = "ERROR"
        self.fields['ContextForDurations'] = "ERROR"

        # This finds the period end date for the database table, and instant
        # date (for balance sheet):
        UseContext = "ERROR"
        #EndDate = self.getNode("//dei:DocumentPeriodEndDate").text
        # This is the <instant> or the <endDate>

        # Uses the concept ASSETS to find the correct instance context
        # This finds the Context ID for that end date (has correct <instant>
        # date plus has no dimensions):
        oNodelist2 = self.getNodeList(
            "//us-gaap:Assets | //us-gaap:AssetsCurrent | //us-gaap:LiabilitiesAndStockholdersEquity")

        # Nodelist of all the facts which are us-gaap:Assets
        for i in oNodelist2:
            ContextID = i.get('contextRef')
            ContextPeriod = self.getNode(
                "//xbrli:context[@id='" + ContextID + "']/xbrli:period/xbrli:instant").text

            # Nodelist of all the contexts of the fact us-gaap:Assets
            oNodelist3 = self.getNodeList(
                "//xbrli:context[@id='" + ContextID + "']")
            for j in oNodelist3:

                # Nodes with the right period
                if self.getNode("xbrli:period/xbrli:instant", j) is not None and self.getNode("xbrli:period/xbrli:instant", j).text == EndDate:

                    oNode4 = self.getNodeList(
                        "xbrli:entity/xbrli:segment/xbrldi:explicitMember", j)

                    if not len(oNode4):
                        UseContext = ContextID

        ContextForInstants = UseContext
        self.fields['ContextForInstants'] = ContextForInstants

        # This finds the duration context
        # This may work incorrectly for fiscal year ends because the dates cross calendar years
        # Get context ID of durations and the start date for the database table
        oNodelist2 = self.getNodeList(
            "//us-gaap:CashAndCashEquivalentsPeriodIncreaseDecrease | //us-gaap:CashPeriodIncreaseDecrease | //us-gaap:NetIncomeLoss | //dei:DocumentPeriodEndDate")

        StartDate = "ERROR"
        StartDateYTD = "2099-01-01"
        UseContext = "ERROR"

        for i in oNodelist2:
            ContextID = i.get('contextRef')
            ContextPeriod = self.getNode("//xbrli:context[@id='" + ContextID + "']/xbrli:period/xbrli:endDate")

            # Nodelist of all the contexts of the fact us-gaap:Assets
            oNodelist3 = self.getNodeList(
                "//xbrli:context[@id='" + ContextID + "']")
            for j in oNodelist3:

                # Nodes with the right period
                if self.getNode("xbrli:period/xbrli:endDate", j).text == EndDate:

                    oNode4 = self.getNodeList(
                        "xbrli:entity/xbrli:segment/xbrldi:explicitMember", j)

                    # Making sure there are no dimensions. Is this the right
                    # way to do it?
                    if not len(oNode4):

                        # Get the year-to-date context, not the current period
                        StartDate = self.getNode("xbrli:period/xbrli:startDate", j).text

                        if StartDate <= StartDateYTD:
                            # Context start date is less than current year to date
                            StartDateYTD = StartDate
                            UseContext = j.get('id')
                        else:
                            # Start date is for year
                            StartDateYTD = StartDateYTD

        # Balance sheet date of current period
        self.fields['BalanceSheetDate'] = EndDate

        # MsgBox "Instant context is: " + ContextForInstants
        if ContextForInstants == "ERROR":
            # MsgBox "Looking for alternative instance context"

            ContextForInstants = self.LookForAlternativeInstanceContext()
            self.fields['ContextForInstants'] = ContextForInstants

        # Income statement date for current fiscal year, year to date
        self.fields['IncomeStatementPeriodYTD'] = StartDateYTD

        ContextForDurations = UseContext
        self.fields['ContextForDurations'] = ContextForDurations

    def LookForAlternativeInstanceContext(self):
        # This deals with the situation where no instance context has no dimensions
        # Finds something

        something = None

        # See if there are any nodes with the document period focus date
        oNodeList_Alt = self.getNodeList(
            "//xbrli:context[xbrli:period/xbrli:instant='" + self.fields['BalanceSheetDate'] + "']")

        # MsgBox "Node list length: " + oNodeList_Alt.length
        for oNode_Alt in oNodeList_Alt:
            # Found possible contexts
            # MsgBox oNode_Alt.selectSingleNode("@id").text
            something = self.getNode(
                "//us-gaap:Assets[@contextRef='" + oNode_Alt.get("id") + "']")
            if something:
                # MsgBox "Use this context: " +
                # oNode_Alt.selectSingleNode("@id").text
                return oNode_Alt.get("id")
