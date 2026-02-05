from typing import List
from app.models import DigestPost
from datetime import datetime


def generate_digest_html(posts: List[DigestPost], is_preview: bool = False) -> str:
    """Generate HTML email template for digest."""

    # Generate posts HTML
    posts_html = ""
    for i, post in enumerate(posts, 1):
        posts_html += f"""
        <div style="margin-bottom: 30px; padding-bottom: 30px; border-bottom: 1px solid #e5e7eb;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="background: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; margin-right: 8px;">
                    r/{post.subreddit}
                </span>
                <span style="color: #6b7280; font-size: 12px;">
                    {post.score} upvotes • {post.num_comments} comments
                </span>
            </div>
            <h3 style="margin: 8px 0; font-size: 18px; line-height: 1.4;">
                <a href="{post.url}" style="color: #111827; text-decoration: none;">
                    {post.title}
                </a>
            </h3>
            <p style="color: #4b5563; font-size: 14px; line-height: 1.6; margin: 8px 0 0 0;">
                {post.summary}
            </p>
        </div>
        """

    preview_banner = ""
    if is_preview:
        preview_banner = """
        <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px 16px; margin-bottom: 20px; border-radius: 4px;">
            <strong style="color: #92400e;">Preview Mode</strong>
            <p style="color: #92400e; margin: 4px 0 0 0; font-size: 14px;">This is a preview. Posts will not be marked as sent.</p>
        </div>
        """

    date_str = datetime.now().strftime("%A, %B %d, %Y")

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="color-scheme" content="light dark">
        <meta name="supported-color-schemes" content="light dark">
        <title>Your Reddit Digest</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f9fafb;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f9fafb; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <tr>
                            <td style="padding: 40px;">
                                {preview_banner}
                                <div style="text-align: center; margin-bottom: 30px;">
                                    <h1 style="margin: 0 0 8px 0; font-size: 28px; color: #111827;">
                                        Your Reddit Digest
                                    </h1>
                                    <p style="margin: 0; color: #6b7280; font-size: 14px;">
                                        {date_str}
                                    </p>
                                </div>

                                <div style="margin-top: 30px;">
                                    {posts_html}
                                </div>

                                <div style="margin-top: 40px; padding-top: 30px; border-top: 1px solid #e5e7eb; text-align: center;">
                                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                                        You're receiving this digest because you configured Reddit Summarizer.
                                    </p>
                                    <p style="color: #9ca3af; font-size: 12px; margin: 8px 0 0 0;">
                                        Manage your preferences in the dashboard.
                                    </p>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

        <style>
            @media (prefers-color-scheme: dark) {{
                body {{
                    background-color: #111827 !important;
                }}
                table[style*="background-color: white"] {{
                    background-color: #1f2937 !important;
                }}
                h1, h3, a {{
                    color: #f9fafb !important;
                }}
                p {{
                    color: #d1d5db !important;
                }}
            }}
        </style>
    </body>
    </html>
    """

    return html
