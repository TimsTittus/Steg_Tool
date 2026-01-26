import streamlit.components.v1 as components

def clipboard_button(text, label="Copy Key"):
    safe_text = text.replace("'", "&#39;").replace('"', '&quot;')
    components.html(f'''
        <button id="copy-btn" onclick="navigator.clipboard.writeText('{safe_text}').then(function(){{ showCopied(); }});" style="padding:6px 16px;font-size:16px;cursor:pointer;background:#F44336;color:white;border:none;border-radius:4px;">{label}</button>
        <span id="copied-msg" style="display:none;margin-left:10px;color:#F44336;font-weight:bold;">Copied!</span>
        <script>
        function showCopied(){{
            var msg = document.getElementById('copied-msg');
            msg.style.display = 'inline';
            setTimeout(function(){{ msg.style.display = 'none'; }}, 1200);
        }}
        </script>
    ''', height=40)
