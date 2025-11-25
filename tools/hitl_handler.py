"""
TODO 1: intergrate
        async def _phase_4_hitl(self, gaps):
        ""HITL checkpoint with real user input for terminal mode""
        logger.info("=" * 60)
        logger.info("HITL CHECKPOINT - Pausing for user input")
        logger.info("=" * 60)

        approval = self.hitl.request_search_approval(gaps)

        self.research_state['user_interactions'].append({
            'type': 'search_approval',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message': approval['message']
        })

        logger.info("\n" + approval['message'])

        if os.getenv('HITL_MODE') == 'terminal' and sys.stdin.isatty():
            print("\n" + "=" * 60)
            print("⏸️  HUMAN INPUT REQUIRED")
            print("=" * 60)
            print(approval['message'])
            print("\nOptions:")
            for idx, opt in enumerate(approval['options'], 1):
                print(f"  {idx}. {opt}")

            while True:
                choice = input("\n👉 Enter your choice (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    break
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

            if choice == '1':
                decision = {
                    'continue_search': True,
                    'modified_queries': [gap['suggested_query'] for gap in gaps.get('critical_gaps', [])],
                    'user_feedback': 'User chose: Continue with suggested searches'
                }
            elif choice == '2':
                print("\n📝 Enter your modified search strategy:")
                custom_query = input("Search query: ").strip()
                decision = {
                    'continue_search': True,
                    'modified_queries': [custom_query],
                    'user_feedback': f'User provided custom query: {custom_query}'
                }
            elif choice == '3':
                decision = {
                    'continue_search': False,
                    'user_feedback': 'User chose: Stop and synthesize'
                }
            else:
                print("\n📝 Enter custom search query:")
                custom_query = input("Query: ").strip()
                decision = {
                    'continue_search': True,
                    'modified_queries': [custom_query] + [gap['suggested_query'] for gap in gaps.get('critical_gaps', [])],
                    'user_feedback': f'User added custom query: {custom_query}'
                }

            print(f"\n✅ {decision['user_feedback']}")
            print("=" * 60)
        else:
            logger.warning("HITL_MODE not terminal or stdin not TTY - using simulated response")
            decision = {
                'continue_search': True,
                'modified_queries': [gap['suggested_query'] for gap in gaps.get('critical_gaps', [])],
                'user_feedback': 'Simulated: Continue (set HITL_MODE=terminal for real input)'
            }

        logger.info(f"USER DECISION: {decision['user_feedback']}")
        logger.info("=" * 60)

        return decision
    
"""
"""
TODO 2: update instruction to include HITL steps and user notification requirements
"""