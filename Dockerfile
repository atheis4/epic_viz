FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
		python python-dev python-pip python-virtualenv \
		build-essential \
		mysql-client libmysqlclient-dev \
		sqlite3 \
		apache2 apache2-dev \
		libhdf5-serial-dev

RUN easy_install pip
RUN pip install --upgrade distribute

RUN pip install mysqlclient

COPY . /epic_viz
RUN pip install -r /epic_viz/requirements.txt

RUN pip install db-tools -i http://dev-tomflem.ihme.washington.edu/simple --trusted-host dev-tomflem.ihme.washington.edu

EXPOSE 8000
