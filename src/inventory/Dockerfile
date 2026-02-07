FROM alpine:3.20

# Inventory service - tracks product stock levels and availability.
RUN adduser -D -u 10001 app
USER 10001

CMD ["sh", "-lc", "echo 'inventory service starting...' && sleep 3600"]

