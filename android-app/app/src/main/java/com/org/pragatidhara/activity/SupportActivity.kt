package com.org.pragatidhara.activity

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView
import com.org.pragatidhara.R

class SupportActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_support)

        // Back navigation from header
        val ivBack = findViewById<ImageView?>(R.id.iv_back)
        ivBack?.setOnClickListener { finish() }

        // Populate user name (from intent if available, otherwise default)
        val tvUserName = findViewById<TextView?>(R.id.tv_user_name)
        val userName = intent.getStringExtra("userName") ?: getString(R.string.nav_header_name)
        tvUserName?.text = userName

        // FAQ card click -> show help (placeholder)
        val cardFaqs = findViewById<CardView?>(R.id.card_faqs)
        cardFaqs?.setOnClickListener {
            // TODO: replace with real FAQ screen / webview
            Toast.makeText(this, "Open FAQs & Help Articles", Toast.LENGTH_SHORT).show()
        }

        // Live chat card click -> open chat (placeholder)
        val cardLive = findViewById<CardView?>(R.id.card_livechat)
        cardLive?.setOnClickListener {
            // TODO: replace with real live chat integration
            Toast.makeText(this, "Starting Live Chat...", Toast.LENGTH_SHORT).show()
        }

        // Submit request handling
        val etIssue = findViewById<EditText?>(R.id.et_issue)
        val btnSubmit = findViewById<Button?>(R.id.btn_submit_request)
        btnSubmit?.setOnClickListener {
            val issue = etIssue?.text?.toString()?.trim().orEmpty()
            if (issue.isEmpty()) {
                Toast.makeText(this, "Please describe your issue before submitting", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Show confirmation dialog
            AlertDialog.Builder(this)
                .setTitle("Submit Request")
                .setMessage("Submit this request to support?\n\n" + issue)
                .setPositiveButton("Submit") { _, _ ->
                    Toast.makeText(this, "Request submitted. We'll get back to you shortly.", Toast.LENGTH_LONG).show()
                    etIssue?.setText("")
                }
                .setNegativeButton("Cancel", null)
                .show()
        }
    }
}
