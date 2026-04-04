import gradio as gr
from environment.core import EmailTriageEnv
from baseline.inference import RuleBasedAgent

env = None
agent = RuleBasedAgent()

def reset_env(task):
    global env
    env = EmailTriageEnv(task)
    obs = env.reset()
    return format_email(obs), f"✅ Ready! Task: {task} | Emails: {len(env.task.emails)}"

def take_action(action):
    global env
    if env is None:
        return "⚠️ Please reset the environment first", "Error: No environment"
    
    action_dict = {"type": action, "reasoning": "User selected action"}
    obs, reward, done, info = env.step(action_dict)
    
    status = f"📝 Action: {action} | Reward: {reward:.2f}"
    
    if done:
        final_score = env.task.compute_final_score(env.actions_taken)
        status += f"\n\n🎉 Episode Complete!\n📊 Final Score: {final_score:.2f}\n✅ Task: {env.task.name} finished!"
    
    return format_email(obs), status

def format_email(obs):
    email = obs.current_email
    
    # Create a visual progress bar
    progress = obs.metrics.get('progress', 0)
    progress_bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
    
    return f"""
╔══════════════════════════════════════════════════════════════╗
║                      📧 CURRENT EMAIL                        ║
╠══════════════════════════════════════════════════════════════╣
║ From: {email.from_address:<52} ║
║ Subject: {email.subject[:50]:<52} ║
╠══════════════════════════════════════════════════════════════╣
║ Body:                                                       ║
║ {email.body[:300]}...                                       ║
╠══════════════════════════════════════════════════════════════╣
║ 📊 METRICS                                                  ║
╠══════════════════════════════════════════════════════════════╣
║ Urgency: {obs.metrics.get('urgency_score', 0):.2f}     Importance: {obs.metrics.get('importance_score', 0):.2f}      ║
║ Progress: [{progress_bar}] {progress:.0%}                         ║
║ Queue: {obs.inbox_queue} remaining    Time: {obs.time_remaining:.0%}                     ║
╚══════════════════════════════════════════════════════════════╝
"""

# Create Gradio interface
with gr.Blocks(title="Email Triage Environment", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 📧 Email Triage Assistant Environment
    
    **Real-world executive email management simulation**
    
    Prioritize and categorize emails just like a real administrative assistant!
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            task_selector = gr.Dropdown(
                choices=[
                    ("Easy - Basic Priority", "easy_triage"),
                    ("Medium - Multi-constraint", "medium_triage"), 
                    ("Hard - Complex Stakeholders", "hard_triage")
                ],
                value="easy_triage",
                label="📋 Select Task Difficulty"
            )
            reset_btn = gr.Button("🔄 Reset Environment", variant="primary", size="lg")
            
            gr.Markdown("---")
            gr.Markdown("### 🎯 Available Actions")
            gr.Markdown("Click any button to take action on the current email:")
            
            # Create action buttons in groups
            with gr.Group():
                gr.Markdown("**Priority Actions**")
                with gr.Row():
                    high_btn = gr.Button("🔴 Prioritize High", variant="stop")
                    normal_btn = gr.Button("🟡 Prioritize Normal")
                    low_btn = gr.Button("🟢 Prioritize Low")
            
            with gr.Group():
                gr.Markdown("**Category Actions**")
                with gr.Row():
                    urgent_btn = gr.Button("⚠️ Categorize Urgent")
                    regular_btn = gr.Button("📄 Categorize Regular")
                    info_btn = gr.Button("ℹ️ Categorize Informational")
            
            with gr.Group():
                gr.Markdown("**Management Actions**")
                with gr.Row():
                    delegate_btn = gr.Button("🤝 Delegate")
                    archive_btn = gr.Button("📦 Archive")
                    request_btn = gr.Button("❓ Request Info")
        
        with gr.Column(scale=2):
            email_display = gr.Textbox(
                label="Current Email",
                lines=25,
                max_lines=30,
                elem_id="email_box"
            )
            status_display = gr.Textbox(
                label="Status / Feedback",
                lines=5,
                interactive=False
            )
    
    # Connect buttons to functions
    reset_btn.click(reset_env, inputs=[task_selector], outputs=[email_display, status_display])
    
    # Priority buttons
    high_btn.click(lambda: "prioritize_high", outputs=None).then(
        take_action, inputs=[high_btn], outputs=[email_display, status_display]
    )
    normal_btn.click(lambda: "prioritize_normal", outputs=None).then(
        take_action, inputs=[normal_btn], outputs=[email_display, status_display]
    )
    low_btn.click(lambda: "prioritize_low", outputs=None).then(
        take_action, inputs=[low_btn], outputs=[email_display, status_display]
    )
    
    # Category buttons
    urgent_btn.click(lambda: "categorize_urgent", outputs=None).then(
        take_action, inputs=[urgent_btn], outputs=[email_display, status_display]
    )
    regular_btn.click(lambda: "categorize_regular", outputs=None).then(
        take_action, inputs=[regular_btn], outputs=[email_display, status_display]
    )
    info_btn.click(lambda: "categorize_informational", outputs=None).then(
        take_action, inputs=[info_btn], outputs=[email_display, status_display]
    )
    
    # Management buttons
    delegate_btn.click(lambda: "delegate", outputs=None).then(
        take_action, inputs=[delegate_btn], outputs=[email_display, status_display]
    )
    archive_btn.click(lambda: "archive", outputs=None).then(
        take_action, inputs=[archive_btn], outputs=[email_display, status_display]
    )
    request_btn.click(lambda: "request_info", outputs=None).then(
        take_action, inputs=[request_btn], outputs=[email_display, status_display]
    )
    
    # Load initial state
    demo.load(reset_env, inputs=[task_selector], outputs=[email_display, status_display])

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Starting Email Triage Web Interface")
    print("="*50)
    print("\n📱 Open your browser and go to: http://localhost:7860")
    print("⌨️  Press Ctrl+C to stop the server\n")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
