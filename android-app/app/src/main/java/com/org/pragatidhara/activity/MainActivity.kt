package com.org.pragatidhara.activity

import android.content.Intent
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import com.google.android.material.navigation.NavigationView
import com.org.pragatidhara.R

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Drawer and navigation view
        val drawer = findViewById<DrawerLayout>(R.id.drawer_layout)
        val navView = findViewById<NavigationView>(R.id.navigation_view)

        // Populate nav header (customer icon + name)
        navView?.let { nv ->
            val header = nv.getHeaderView(0)
            val tvName = header.findViewById<TextView>(R.id.nav_header_name)
            val tvMobile = header.findViewById<TextView>(R.id.nav_header_sub)
            // If your app has a logged-in user, replace these with real values
            tvName?.text = getString(R.string.nav_header_name)
            tvMobile?.text = getString(R.string.nav_header_mobile)
        }

        // Use the header LinearLayout from activity_main.xml (iv_menu, iv_small_logo, tv_app_title)
        val header = findViewById<LinearLayout?>(R.id.header)
        header?.let {
            val ivMenu = it.findViewById<ImageView>(R.id.iv_menu)
            ivMenu.contentDescription = getString(R.string.open_navigation)
            ivMenu.setOnClickListener {
                // open navigation drawer
                drawer.openDrawer(GravityCompat.START)
            }

            val ivLogo = it.findViewById<ImageView>(R.id.iv_small_logo)
            ivLogo.setOnClickListener {
                Toast.makeText(this, "Logo clicked", Toast.LENGTH_SHORT).show()
            }

            val tvTitle = it.findViewById<TextView>(R.id.tv_app_title)
            tvTitle.text = getString(R.string.screen_title)
        }

        // Handle navigation item clicks
        navView.setNavigationItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.nav_find_route -> {
                    // already in MainActivity - close drawer
                    drawer.closeDrawer(GravityCompat.START)
                    true
                }
                R.id.nav_vehicle_details -> {
                    val intent = Intent(this, VehicleDetailsActivity::class.java)
                    startActivity(intent)
                    drawer.closeDrawer(GravityCompat.START)
                    menuItem.isChecked = true
                    true
                }
                R.id.nav_rewards -> {
                    val intent = Intent(this, RewardsActivity::class.java)
                    startActivity(intent)
                    drawer.closeDrawer(GravityCompat.START)
                    menuItem.isChecked = true
                    true
                }
                R.id.nav_support -> {
                    val intent = Intent(this, SupportActivity::class.java)
                    startActivity(intent)
                    drawer.closeDrawer(GravityCompat.START)
                    menuItem.isChecked = true
                    true
                }
                else -> {
                    drawer.closeDrawer(GravityCompat.START)
                    false
                }
            }
        }
    }

    override fun onBackPressed() {
        val drawer = findViewById<androidx.drawerlayout.widget.DrawerLayout?>(R.id.drawer_layout)
        if (drawer != null && drawer.isDrawerOpen(androidx.core.view.GravityCompat.START)) {
            drawer.closeDrawer(androidx.core.view.GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate menu (expects res/menu/menu_main.xml to exist)
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_notifications -> {
                Toast.makeText(this, "Notifications", Toast.LENGTH_SHORT).show()
                true
            }
            R.id.action_search -> {
                Toast.makeText(this, "Search", Toast.LENGTH_SHORT).show()
                true
            }
            R.id.action_more -> {
                Toast.makeText(this, "More", Toast.LENGTH_SHORT).show()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }
}