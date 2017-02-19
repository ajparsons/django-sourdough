from files import QuickGrid, FlexiBook
from datetime import datetime,timedelta
from collections import Counter
import sys

class RequestRange(object):
    """
    create statistics from a set of requests
    """
    def __init__(self,requests):
        self.requests = requests
        
    def limit(self,range):
        """
        pass a list of two datetime objects to set a range
        """
        self.requests = [x for x in self.requests if x.in_range(range)]
        self.requests.sort(key=lambda x:x.date)

    def total_foi(self):
        """
        total foi requests
        """
        return len(self.requests)
    
    def user_ids(self):
        """
        return ql of all unique user ids
        """
        ids = list(set([x.user for x in self.requests]))
        q = QuickGrid("Ids")
        q.header = ["Id"]
        q.data = [[x] for x in ids]
        return q
                
    def total_unique_users(self):
        """
        int of number of unique users
        """
        return len(set([x.user for x in self.requests]))
    
    def status(self):
        """
        returns qg of how the requests breakdown by status
        """
        q = QuickGrid("Status")
        q.header = ["Status","Count"]
        
        def fix_status(s):
            n = s.replace("_"," ")
            n = s.title()
            return n
        
        status = [fix_status(x.status) for x in self.requests]
        
        c = Counter(status)
        q.data = [[x for x in y] for y in c.iteritems()]
        q.data.sort(key=lambda x:x[1],reverse=True)
        
        total = sum([x["count"] for x in q])
        q.header.append("percentage")
        for r in q:
            p = round((float(r["count"])/total) * 100,2)
            r.append(p)
        
        return q

    
    def alt_month(self):
        """
        returns breakdown by month period - but in 23-23 intervals rather than calendar months
        """
        
        options = [[x-6,[datetime(2016,x,23),datetime(2016,x + 1, 23)]] for x in range(3,9)]

        q = QuickGrid("By Month")
        q.header = ["Month","Total Requests","Total Unique Users"]
        
        for o in options:

            month_requests = RequestRange(self.requests)
            month_requests.limit(o[1])
            q.data.append(["T{0}:T{1}".format(o[0],o[0]+1),
                           month_requests.total_foi(),
                           month_requests.total_unique_users()
                           ])
        
        return q
        
    def weeks(self):
        """
        returns a qg with breakdown of requests per week
        """
        return self.days("By Week","%YW%U")
        
    
    def days(self,sheet_name="By Day",format="%Y-%m-%d"):
        """
        returns qg with breakdown of requests per day
        """
        q = QuickGrid(sheet_name)
        q.header = ["Date","Count"]
        
        results = [r.date.strftime(format) for r in self.requests]
        c = Counter(results)
        cc = [[x for x in y] for y in c.iteritems()]
        cc.sort(key=lambda x:x[0])
        q.data = cc
        
        return q
    
    def months(self):
        """
        breakdown of requests per calendar month
        """
        start_month,start_year = self.requests[0].date.month, self.requests[0].date.year
        end_month,end_year = self.requests[-1].date.month, self.requests[-1].date.year
        
        month,year = start_month,start_year
        end = False
        
        q = QuickGrid("By Month")
        q.header = ["Month","Total Requests","Total Unique Users"]
        
        while end == False:
            month += 1
            if month == 13:
                month = 1
                year += 1
            if year == end_year and month == end_month:
                end = True
            
            start = datetime(year,month,1)
            if month == 12:
                endr = datetime(year+1,1,1)
            else:
                endr = datetime(year,month+1,1)
            
            range = [start,endr]
            month_requests = RequestRange(self.requests)
            month_requests.limit(range)
            q.data.append(["{0}-{1}".format(month,year),
                           month_requests.total_foi(),
                           month_requests.total_unique_users()
                           ])
        
        return q
            
    def exclude_single_matches(self,excludes):
        """
        remove requests that only match any of the items in the excludes list
        """
        packaged = [[x] for x in excludes]
        self.requests = [x for x in self.requests if x.matched not in packaged]

    def if_includes(self,includes):
        """
        only retain request that match only one of ite items in the excludes list
        """
        s_includes = set(includes)
        
        def match(matched):
            return s_includes.intersection(set(matched))
        
        self.requests = [x for x in self.requests if match(x.matched)]

    def only_single_matches(self,includes):
        """
        only retain request that match only one of ite items in the excludes list
        """
        packaged = [[x] for x in includes]
        self.requests = [x for x in self.requests if x.matched in packaged]
    
    def multi_requests(self):
        """
        count of how many do multiple requests
        """
        c = Counter([x.user for x in self.requests])
        for x,y in c.iteritems():
            if y > 1:
                print x,y
        c = list(c.itervalues())
        
        cc = Counter(c)
        c = [[x for x in y] for y in cc.iteritems()]
        c.sort()
        q = QuickGrid("Multi Requests")
        q.header = ["No of FOI requests","No of users who made this many requests"]
        
        q.data = c
        
        total = sum([x["No of users who made this many requests"] for x in q])
        q.header.append("percentage")
        for r in q:
            p = round((float(r["No of users who made this many requests"])/total) * 100,2)
            r.append(p)
        
        
        return q
        

class Request(object):
    """
    stores details of all matched
    """
    def __init__(self,header,row):
        self.date = row["date"]
        self.url = row["url"]
        self.status = row["status"]
        self.user = row["userid"]
        self.matched = []
        for h in header[4:]:
            if row[h]:
                self.matched.append(h)
        self.match_count = len(self.matched)

    def in_range(self,range):
        """
        only in range
        """
        return self.date > range[0] and self.date <= range[1]

def render():
    
    ranges = [
              ("year",[datetime(2015,5,7),datetime(2016,6,23)]),
              #("joined",[datetime(2016,3,24),datetime(2016,9,23)]),  
              #("post",[datetime(2016,6,24),datetime(2016,9,23)]),  
              #("pre",[datetime(2016,3,24),datetime(2016,6,23)]),
              #("month",[datetime(2016,6,23),datetime(2016,7,23)]),
              #("pre_post_month",[datetime(2016,6,5),datetime(2016,8,23)]),
               ]
    
    
    for r in ranges:
    
        # load requests
        q = QuickGrid().open("F:\\mysociety\\eu-export.xlsx")
        
        rr = RequestRange([Request(q.header,x) for x in q])
        rr.limit(r[1])
        
        #rr.if_includes(["Immigration"])
        ##rr.only_single_matches(["Immigration"])
        rr.exclude_single_matches(["Immigration","Migration"])
        
        headline = QuickGrid("Headline")
        headline.header = ["Total FOI","Unique Users"]
        headline.data = [[rr.total_foi(),rr.total_unique_users()]]
        
        multi_requests = rr.multi_requests()
        status = rr.status()
        if r[0] == "joined":
            months = rr.alt_month()
        else:
            months = rr.months()
            
            
        days = rr.days()
        weeks = rr.weeks()
        ids = rr.user_ids()
        #save FlexiBook
        f = FlexiBook()
        f.add_sheet_from_ql(headline)
        f.add_sheet_from_ql(multi_requests)
        f.add_sheet_from_ql(status)
        f.add_sheet_from_ql(months)
        f.add_sheet_from_ql(days)
        f.add_sheet_from_ql(weeks)
        f.add_sheet_from_ql(ids)
        file_name = "F:\\mysociety\\imm_2_results-{0}.xls".format(r[0])
        #f.save(file_name)
        print "saving {0}".format(file_name)
        

render()