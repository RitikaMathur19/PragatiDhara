package com.org.pragatidhara.activity

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.org.pragatidhara.databinding.ActivityUserNameBinding

class UserNameActivity : AppCompatActivity() {

    private lateinit var binding: ActivityUserNameBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityUserNameBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.btnContinue.setOnClickListener {
            val fullName = binding.etFullName.text.toString().trim()
            if (fullName.isNotEmpty()) {
                val intent = Intent(this, OtpVerificationActivity::class.java)
                intent.putExtra("fullName", fullName)
                startActivity(intent)
            } else {
                binding.etFullName.error = "Please enter your full name"
            }
        }
    }
}