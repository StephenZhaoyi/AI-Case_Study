.PHONY: chat admin run-all stop

chat:
	streamlit run src/pages/chat_app.py --server.port 8501

admin:
	streamlit run src/pages/admin_app.py --server.port 8502

run-all: stop
	@streamlit run src/pages/chat_app.py --server.port 8501 > /tmp/chat_app.log 2>&1 & echo $$! > /tmp/chat_app.pid
	@streamlit run src/pages/admin_app.py --server.port 8502 > /tmp/admin_app.log 2>&1 & echo $$! > /tmp/admin_app.pid
	@echo "Chat: http://localhost:8501"
	@echo "Admin: http://localhost:8502"

stop:
	-@if [ -f /tmp/chat_app.pid ]; then kill "$(cat /tmp/chat_app.pid)" 2>/dev/null || true; rm -f /tmp/chat_app.pid; fi
	-@if [ -f /tmp/admin_app.pid ]; then kill "$(cat /tmp/admin_app.pid)" 2>/dev/null || true; rm -f /tmp/admin_app.pid; fi
	-@pkill -f "[s]treamlit run src/pages/chat_app.py --server.port 8501" || true
	-@pkill -f "[s]treamlit run src/pages/admin_app.py --server.port 8502" || true
