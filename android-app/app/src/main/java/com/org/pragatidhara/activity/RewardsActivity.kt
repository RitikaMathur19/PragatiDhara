package com.org.pragatidhara.activity

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.org.pragatidhara.R
import com.org.pragatidhara.databinding.ActivityRewardsBinding
import com.org.pragatidhara.databinding.ActivityVehicleDetailsBinding

class RewardsActivity : AppCompatActivity() {

    private lateinit var binding: ActivityRewardsBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityRewardsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        // Back navigation for header back icon (if present in layout)
        val ivBack = findViewById<android.widget.ImageView?>(R.id.iv_back)
        ivBack?.setOnClickListener { finish() }

    }
}