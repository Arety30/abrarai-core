import sys
import os
import threading
import customtkinter as ctk

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.abrar_ai_1 import AbrarOrchestrator

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernAbrarUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ABRARAI // System Orchestrator")
        self.geometry("1100x750")
        self.minsize(950, 600)
        
        # Initialize Backend Engine
        self.engine = AbrarOrchestrator()

        # Layout Configuration (Sidebar + Main Chat Area)
        self.grid_columnconfigure(0, weight=0) # Sidebar fixed
        self.grid_columnconfigure(1, weight=1) # Chat expands
        self.grid_rowconfigure(0, weight=1)

        # ---------------- SIDEBAR NAVIGATION ----------------
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#1a1c1e")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # App Title
        self.logo_label = ctk.CTkLabel(self.sidebar, text="ABRARAI Core", font=("Segoe UI", 22, "bold"), text_color="#5294e2")
        self.logo_label.pack(padx=20, pady=(30, 20), anchor="w")

        # Telemetry Dashboard Section
        self.stats_frame = ctk.CTkFrame(self.sidebar, fg_color="#25282c", corner_radius=8)
        self.stats_frame.pack(padx=15, pady=10, fill="x")
        
        self.tier_lbl = ctk.CTkLabel(self.stats_frame, text=f"COMPUTE TIER: {self.engine.compute_tier}", font=("Consolas", 12, "bold"), text_color="#2ecc71" if self.engine.compute_tier != "LITE" else "#f1c40f")
        self.tier_lbl.pack(padx=10, pady=8, anchor="w")
        
        self.os_lbl = ctk.CTkLabel(self.stats_frame, text=f"HOST: Ubuntu Linux", font=("Consolas", 11), text_color="#aaaaaa")
        self.os_lbl.pack(padx=10, pady=(0, 8), anchor="w")

        # Action Buttons
        self.clear_btn = ctk.CTkButton(self.sidebar, text="Clear Session", fg_color="#e74c3c", hover_color="#c0392b", font=("Segoe UI", 12, "bold"), command=self.clear_chat)
        self.clear_btn.pack(padx=15, pady=(20, 0), fill="x", side="bottom")

        # ---------------- MAIN CHAT WORKSPACE ----------------
        self.main_workspace = ctk.CTkFrame(self, fg_color="#202225", corner_radius=0)
        self.main_workspace.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_workspace.grid_columnconfigure(0, weight=1)
        self.main_workspace.grid_rowconfigure(0, weight=1) # Chat window expands
        self.main_workspace.grid_rowconfigure(1, weight=0) # Entry fixed at bottom

        # Chat Text Canvas
        self.chat_display = ctk.CTkTextbox(self.main_workspace, state="disabled", wrap="word", font=("Segoe UI", 14), fg_color="#23272a", border_color="#2f3136", border_width=1)
        self.chat_display.grid(row=0, column=0, padx=25, pady=(25, 15), sticky="nsew")

        # Bottom Input Dock
        self.input_dock = ctk.CTkFrame(self.main_workspace, fg_color="transparent")
        self.input_dock.grid(row=1, column=0, padx=25, pady=(0, 25), sticky="ew")
        self.input_dock.grid_columnconfigure(0, weight=1)

        # Control Entry
        self.entry = ctk.CTkEntry(self.input_dock, placeholder_text="Send a message or invoke system control...", font=("Segoe UI", 14), height=45, fg_color="#2c2f33", border_color="#40444b", text_color="#ffffff")
        self.entry.grid(row=0, column=0, padx=(0, 15), sticky="ew")
        self.entry.bind("<Return>", self.trigger_send)

        # High-Tech Action Button
        self.send_btn = ctk.CTkButton(self.input_dock, text="RUN", font=("Segoe UI", 13, "bold"), height=45, width=110, fg_color="#3498db", hover_color="#2980b9", command=self.trigger_send)
        self.send_btn.grid(row=0, column=1)

        self.write_to_display("SYSTEM", "Core infrastructure routing online. Ready to build.", "#5294e2")

    def write_to_display(self, sender, text, color="#ffffff"):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"▶ {sender}\n", "header")
        self.chat_display.insert("end", f"{text}\n\n", "body")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def clear_chat(self):
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
        self.write_to_display("SYSTEM", "Workspace conversation vector flushed clean.", "#5294e2")

    def trigger_send(self, event=None):
        prompt = self.entry.get().strip()
        if not prompt: return
        
        self.entry.delete(0, "end")
        self.write_to_display("YOU", prompt, "#ffffff")
        
        self.entry.configure(state="disabled")
        self.send_btn.configure(state="disabled")
        
        threading.Thread(target=self.offload_execution, args=(prompt,), daemon=True).start()

    def offload_execution(self, prompt):
        try:
            # Check if user input looks like a system command to switch intent types
            intent = "SYSTEM_CONTROL" if prompt.startswith(("ls", "pwd", "mkdir")) else "GENERAL"
            args = {"command": prompt.split()[0], "args": prompt.split()[1:]} if intent == "SYSTEM_CONTROL" else None
            
            result = self.engine.execute_task(intent, prompt, arguments=args)
            
            if "execution_result" in result:
                output = result["execution_result"].get("output") or result["execution_result"].get("error")
                response_text = f"Executed instruction via OSBridge Sandbox:\n\n{output}"
            else:
                response_text = result["response"]

            self.after(0, self.write_to_display, f"ABRAR_AI // {result['model']}", response_text)
        except Exception as err:
            self.after(0, self.write_to_display, "CORE_ERROR", str(err))
        finally:
            self.after(0, lambda: self.entry.configure(state="normal"))
            self.after(0, lambda: self.send_btn.configure(state="normal"))
            self.after(0, self.entry.focus)

if __name__ == "__main__":
    app = ModernAbrarUI()
    app.mainloop()
