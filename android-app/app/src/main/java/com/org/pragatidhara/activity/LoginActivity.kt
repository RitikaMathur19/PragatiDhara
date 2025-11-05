package com.org.pragatidhara.activity

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.org.pragatidhara.databinding.ActivityLoginBinding
class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // initialize view binding and set content view
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.btnLogin.setOnClickListener {
            // Mock login logic
            startActivity(Intent(this, MainActivity::class.java))
            finish()
        }

        binding.btnSignUp.setOnClickListener {
            startActivity(Intent(this, UserNameActivity::class.java))
        }
    }
}