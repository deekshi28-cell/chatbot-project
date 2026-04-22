FROM scratch 
COPY python-portable/ /usr/local/ 
ENV PATH="/usr/local/bin:$PATH" 
